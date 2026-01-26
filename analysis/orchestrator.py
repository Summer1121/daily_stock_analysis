# -*- coding: utf-8 -*-
"""
===================================
A股自选股智能分析系统 - LLM Agent 协调器 (LangGraph 版)
===================================

职责：
1. 使用 LangGraph 协调 SummarizerAgent 和 DecisionAgent 的工作流。
2. 管理从原始新闻到最终分析结果的全过程状态。
"""

import logging
from typing import Optional, Dict, Any, List, TypedDict, Annotated
import operator

from langgraph.graph import StateGraph, END

from config import get_config, Config
from analysis.agents.summarizer import SummarizerAgent
from analysis.agents.decision import DecisionAgent, AnalysisResult
from search_service import SearchService

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """分析工作流的状态定义"""
    stock_code: str
    stock_name: str
    context: Dict[str, Any]  # 包含技术面数据的上下文
    
    # 中间产物
    raw_news: Optional[str]
    news_summary: Optional[str]
    
    # 最终结果
    analysis_result: Optional[AnalysisResult]
    
    # 错误追踪
    errors: Annotated[List[str], operator.add]

class LLMOrchestrator:
    """
    LLM Agent 协调器 (基于 LangGraph)

    负责协调 SummarizerAgent 和 DecisionAgent 的工作流，
    实现从原始新闻搜索、摘要到最终决策分析的完整流程。
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        初始化 LLM 协调器。
        
        Args:
            config: 配置实例，如果未提供则从全局获取。
        """
        self.config = config if config else get_config()
        
        # 初始化 Agents 和服务
        self.summarizer_agent = SummarizerAgent(config=self.config)
        self.decision_agent = DecisionAgent(config=self.config)
        
        self.search_service = SearchService(
            bocha_keys=self.config.bocha_api_keys,
            tavily_keys=self.config.tavily_api_keys,
            serpapi_keys=self.config.serpapi_keys,
        )
        
        # 构建图
        self.workflow = self._build_workflow()
        
        logger.info("LLM 协调器 (LangGraph 版) 初始化完成。")
        if not self.summarizer_agent.is_available():
            logger.warning("摘要 Agent 不可用，新闻摘要功能将受限。")
        if not self.decision_agent.is_available():
            logger.warning("决策 Agent 不可用，核心分析功能将受限。")

    def _build_workflow(self) -> StateGraph:
        """构建 LangGraph 工作流图"""
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("search", self._search_node)
        workflow.add_node("summarize", self._summarize_node)
        workflow.add_node("decision", self._decision_node)
        
        # 设置边
        workflow.set_entry_point("search")
        workflow.add_edge("search", "summarize")
        workflow.add_edge("summarize", "decision")
        workflow.add_edge("decision", END)
        
        return workflow.compile()

    def _search_node(self, state: AgentState) -> Dict[str, Any]:
        """搜索节点：获取原始新闻"""
        code = state["stock_code"]
        name = state["stock_name"]
        
        raw_news_context = None
        if self.search_service.is_available:
            logger.info(f"[{code}] [Workflow] 开始为 {name} 搜索新闻...")
            try:
                intel_results = self.search_service.search_comprehensive_intel(
                    stock_code=code,
                    stock_name=name,
                    max_searches=3
                )
                if intel_results:
                    raw_news_context = self.search_service.format_intel_report(intel_results, name)
                    total_results = sum(len(r.results) for r in intel_results.values() if r.success)
                    logger.info(f"[{code}] [Workflow] 新闻搜索完成，共 {total_results} 条结果。")
            except Exception as e:
                logger.error(f"[{code}] [Workflow] 搜索出错: {e}")
                return {"errors": [f"Search error: {str(e)}"]}
        else:
            logger.info(f"[{code}] [Workflow] 搜索服务不可用，跳过新闻搜索。")

        return {"raw_news": raw_news_context}

    def _summarize_node(self, state: AgentState) -> Dict[str, Any]:
        """摘要节点：对新闻进行摘要"""
        code = state["stock_code"]
        name = state["stock_name"]
        raw_news = state.get("raw_news")
        
        news_summary = None
        if raw_news and self.summarizer_agent.is_available():
            logger.info(f"[{code}] [Workflow] 开始调用摘要 Agent...")
            try:
                news_summary = self.summarizer_agent.summarize(raw_news, code, name)
                if news_summary:
                    logger.info(f"[{code}] [Workflow] 新闻摘要完成。")
                else:
                    logger.warning(f"[{code}] [Workflow] 摘要结果为空，回退到原始新闻。")
                    news_summary = raw_news
            except Exception as e:
                logger.error(f"[{code}] [Workflow] 摘要出错: {e}")
                # 如果摘要失败，回退到原始新闻
                return {"news_summary": raw_news, "errors": [f"Summarization error: {str(e)}"]}
        elif raw_news:
            logger.warning(f"[{code}] [Workflow] 摘要 Agent 不可用，将使用原始新闻。")
            news_summary = raw_news
            
        return {"news_summary": news_summary}

    def _decision_node(self, state: AgentState) -> Dict[str, Any]:
        """决策节点：生成最终分析结果"""
        code = state["stock_code"]
        name = state["stock_name"]
        context = state["context"]
        news_summary = state.get("news_summary")
        
        logger.info(f"[{code}] [Workflow] 开始调用决策 Agent...")
        try:
            final_result = self.decision_agent.analyze(context, news_summary)
            return {"analysis_result": final_result}
        except Exception as e:
            logger.error(f"[{code}] [Workflow] 决策出错: {e}")
            return {"errors": [f"Decision error: {str(e)}"]}

    def analyze(self, 
                context: Dict[str, Any],
                stock_name: str,
                ) -> AnalysisResult:
        """
        执行分析流程（调用 LangGraph）。
        """
        code = context.get('code', 'Unknown')
        
        # 初始化状态
        initial_state: AgentState = {
            "stock_code": code,
            "stock_name": stock_name,
            "context": context,
            "raw_news": None,
            "news_summary": None,
            "analysis_result": None,
            "errors": []
        }
        
        # 执行工作流
        final_state = self.workflow.invoke(initial_state)
        
        # 如果有结果则返回，否则构造一个失败的结果
        if final_state.get("analysis_result"):
            return final_state["analysis_result"]
        
        # 失败处理
        error_msg = "; ".join(final_state.get("errors", ["未知工作流错误"]))
        return AnalysisResult(
            code=code,
            name=stock_name,
            sentiment_score=50,
            trend_prediction='震荡',
            operation_advice='持有',
            success=False,
            error_message=f"工作流执行失败: {error_msg}"
        )
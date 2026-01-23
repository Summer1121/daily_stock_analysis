# -*- coding: utf-8 -*-
"""
===================================
A股自选股智能分析系统 - LLM Agent 协调器
===================================

职责：
1. 协调 SummarizerAgent 和 DecisionAgent 的工作流。
2. 管理从原始新闻到最终分析结果的全过程。
"""

import logging
from typing import Optional, Dict, Any

from config import get_config, Config
from analysis.agents.summarizer import SummarizerAgent
from analysis.agents.decision import DecisionAgent, AnalysisResult
from search_service import SearchService, SearchResponse

logger = logging.getLogger(__name__)


class LLMOrchestrator:
    """
    LLM Agent 协调器

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
        
        logger.info("LLM 协调器初始化完成。 সন")
        if not self.summarizer_agent.is_available():
            logger.warning("摘要 Agent 不可用，新闻摘要功能将受限。")
        if not self.decision_agent.is_available():
            logger.warning("决策 Agent 不可用，核心分析功能将受限。")

    def analyze(self, 
                context: Dict[str, Any],
                stock_name: str,
                ) -> AnalysisResult:
        """
        执行完整的分析流程。

        流程：
        1. 使用 SearchService 搜索原始新闻。
        2. 如果有新闻且摘要 Agent 可用，调用 SummarizerAgent 生成摘要。
        3. 调用 DecisionAgent，传入技术面上下文和新闻摘要。
        4. 返回最终的分析结果。

        Args:
            context (Dict[str, Any]): 包含技术面数据的上下文。
            stock_name (str): 股票名称。

        Returns:
            AnalysisResult: 最终的分析结果。
        """
        code = context.get('code', 'Unknown')
        news_summary = None # 初始化新闻摘要
        
        # Step 1: 搜索原始新闻
        raw_news_context = None
        if self.search_service.is_available:
            logger.info(f"[{code}] [Orchestrator] 开始为 {stock_name} 搜索新闻...")
            intel_results = self.search_service.search_comprehensive_intel(
                stock_code=code,
                stock_name=stock_name,
                max_searches=3
            )
            if intel_results:
                raw_news_context = self.search_service.format_intel_report(intel_results, stock_name)
                total_results = sum(len(r.results) for r in intel_results.values() if r.success)
                logger.info(f"[{code}] [Orchestrator] 新闻搜索完成，共 {total_results} 条结果。")
                logger.debug(f"[{code}] [Orchestrator] 原始新闻内容:\n{raw_news_context}")
        else:
            logger.info(f"[{code}] [Orchestrator] 搜索服务不可用，跳过新闻搜索。 সন")

        # Step 2: 摘要新闻
        if raw_news_context and self.summarizer_agent.is_available():
            logger.info(f"[{code}] [Orchestrator] 开始调用摘要 Agent...")
            news_summary = self.summarizer_agent.summarize(raw_news_context, code, stock_name)
            if news_summary:
                logger.info(f"[{code}] [Orchestrator] 新闻摘要完成。 সন")
                logger.debug(f"[{code}] [Orchestrator] 新闻摘要内容:\n{news_summary}")
elif raw_news_context:
            # 如果摘要 Agent 不可用，直接使用原始新闻（可能会很长）
            logger.warning(f"[{code}] [Orchestrator] 摘要 Agent 不可用，将使用原始新闻进行分析。 সন")
            news_summary = raw_news_context

        # Step 3: 调用决策 Agent
        logger.info(f"[{code}] [Orchestrator] 开始调用决策 Agent...")
        final_result = self.decision_agent.analyze(context, news_summary)
        
        return final_result

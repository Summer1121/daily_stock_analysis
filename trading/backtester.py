# -*- coding: utf-8 -*-
"""
===================================
A股自选股智能分析系统 - 交易回测引擎
===================================

职责：
1. 在历史数据上评估交易策略的有效性。
2. 严格按时间序列模拟交易，杜绝“未来函数”。
3. 生成策略绩效报告。
"""

import logging
import uuid
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path # 导入 Path

import pandas as pd
from sqlalchemy.orm import Session

from config import get_config, Config
from storage import DatabaseManager
from trading.engine import TradingEngine
from analysis.orchestrator import LLMOrchestrator
from analysis.agents.decision import AnalysisResult # 导入AnalysisResult

logger = logging.getLogger(__name__)

class Backtester:
    """
    交易回测引擎
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        初始化回测引擎。

        Args:
            config: 配置实例，如果未提供则从全局获取。
        """
        self.config = config if config else get_config()
        self.db = DatabaseManager.get_instance()
        self.cache_dir = Path("./data/backtest_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"回测引擎初始化完成。缓存目录: {self.cache_dir.absolute()}")

    def _load_historical_data(self, stock_codes: List[str], start_date: date, end_date: date) -> Dict[str, pd.DataFrame]:
        """
        加载历史数据，优先使用文件缓存。
        """
        all_history_data: Dict[str, pd.DataFrame] = {}
        for code in stock_codes:
            cache_filename = f"{code}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pkl"
            cache_path = self.cache_dir / cache_filename

            if cache_path.exists():
                df = pd.read_pickle(cache_path)
                logger.info(f"[{code}] 从缓存文件加载了 {len(df)} 条历史数据。")
            else:
                stock_data = self.db.get_data_range(code, start_date, end_date)
                if stock_data:
                    df = pd.DataFrame([s.to_dict() for s in stock_data])
                    df['date'] = pd.to_datetime(df['date']).dt.date
                    df = df.set_index('date')
                    df.to_pickle(cache_path)
                    logger.info(f"[{code}] 从数据库加载了 {len(df)} 条历史数据，并已缓存。")
                else:
                    df = pd.DataFrame()
            
            if not df.empty:
                all_history_data[code] = df
        
        return all_history_data

    def run(self, 
            stock_codes: List[str], 
            start_date: date, 
            end_date: date
            ) -> Dict[str, Any]:
        """
        运行回测。

        Args:
            stock_codes (List[str]): 要回测的股票代码列表。
            start_date (date): 回测开始日期。
            end_date (date): 回测结束日期。

        Returns:
            Dict[str, Any]: 包含绩效报告的字典。
        """
        session_id = f"backtest_{uuid.uuid4().hex[:8]}"
        logger.info(f"开始回测，会话ID: {session_id}，时间范围: {start_date} 到 {end_date}")

        # 使用新方法加载数据
        all_history_data = self._load_historical_data(stock_codes, start_date, end_date)

        if not all_history_data:
            logger.warning("未加载到任何历史数据，无法进行回测。")
            return {}
        
                daily_assets = []
                current_date = start_date
                
                with self.db.get_session() as session:
                    # 在循环外初始化一次 TradingEngine
                    trading_engine = TradingEngine(
                        db_session=session, 
                        config=self.config,
                        session_id=session_id
                    )
                    orchestrator = LLMOrchestrator(config=self.config)
        
                    while current_date <= end_date:
                        logger.debug(f"--- 回测日期: {current_date} ---")
                        
                        # 更新所有持仓的市价
                        positions = trading_engine.broker.list_positions()
                        for pos in positions:
                            if pos.stock_code in all_history_data and current_date in all_history_data[pos.stock_code].index:
                                current_price = all_history_data[pos.stock_code].loc[current_date]['close']
                                trading_engine.broker._update_position_current_price(pos.stock_code, current_price)
        
                        # 交易决策
                        for code in stock_codes:
                            if code not in all_history_data or current_date not in all_history_data[code].index:
                                continue
        
                            context = self.db.get_analysis_context(code, target_date=current_date)
                            if not context:
                                continue
                            
                            current_price = all_history_data[code].loc[current_date]['close']
                            stock_name = all_history_data[code].loc[current_date].get('name', f"股票{code}")
                            
                            # 运行分析 (在回测中，我们可能跳过新闻搜索以加速，仅依赖技术指标)
                            analysis_result = orchestrator.analyze(context, stock_name)
                            
                            # 执行交易
                            if analysis_result and analysis_result.success:
                                trading_engine.process_analysis(
                                    stock_code=code,
                                    analysis_result=analysis_result,
                                    current_price=current_price,
                                    trade_time=datetime.combine(current_date, datetime.min.time())
                                )
                        
                        # 记录每日总资产
                        balance = trading_engine.broker.get_account_balance()
                        daily_assets.append(balance.total_assets)
                        
                        current_date += timedelta(days=1)
                
                # 生成报告
                report = self.generate_report(session_id, start_date, end_date, daily_assets)
                return report
    def generate_report(self, session_id: str, start_date: date, end_date: date, daily_assets: List[float]) -> Dict[str, Any]:
        """
        生成回测绩效报告。
        """
        logger.info(f"为会话 {session_id} 生成回测报告...")
        
        if not daily_assets:
            return {"error": "没有每日资产数据，无法生成报告。"}

        initial_capital = daily_assets[0]
        final_assets = daily_assets[-1]
        total_return_rate = ((final_assets - initial_capital) / initial_capital) * 100

        # 计算年化回报率
        days = (end_date - start_date).days
        annualized_return = ((1 + total_return_rate / 100) ** (365.0 / days) - 1) * 100 if days > 0 else 0

        # 计算最大回撤
        assets_series = pd.Series(daily_assets)
        cumulative_max = assets_series.cummax()
        drawdown = (assets_series - cumulative_max) / cumulative_max
        max_drawdown = drawdown.min() * 100 if not drawdown.empty else 0

        # 计算夏普比率 (假设无风险利率为0)
        daily_returns = assets_series.pct_change().dropna()
        if not daily_returns.empty and daily_returns.std() != 0:
            sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252) # 假设一年252个交易日
        else:
            sharpe_ratio = 0.0

        return {
            "session_id": session_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "initial_capital": f"{initial_capital:,.2f}",
            "final_assets": f"{final_assets:,.2f}",
            "total_return_rate": f"{total_return_rate:.2f}%",
            "annualized_return": f"{annualized_return:.2f}%",
            "max_drawdown": f"{max_drawdown:.2f}%",
            "sharpe_ratio": f"{sharpe_ratio:.2f}",
        }

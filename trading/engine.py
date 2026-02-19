import logging
from typing import Dict, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from config import Config, get_config
from storage import DatabaseManager
from trading.brokers.base import AbstractBroker
from trading.brokers.paper_broker import PaperBroker # 暂时只使用 PaperBroker
from trading.strategy import BaseStrategy, strategy_registry
from trading.models import Position # 用于类型提示

logger = logging.getLogger(__name__)

class TradingEngine:
    """
    交易引擎类

    负责整合交易策略和经纪商接口，根据分析结果执行交易决策。
    支持模拟交易、实盘交易和回测模式。
    """

    def __init__(self, 
                 db_session: Session, 
                 config: Optional[Config] = None,
                 session_id: str = "default_paper_session",
                 strategy_name: str = "FollowLLMStrategy"
                 ):
        """
        初始化交易引擎。

        Args:
            db_session (Session): SQLAlchemy 数据库会话。
            config (Optional[Config]): 配置实例，如果未提供则从全局获取。
            session_id (str): 模拟或回测会话ID，用于隔离数据。
            strategy_name (str): 要使用的策略名称。
        """
        self.db_session = db_session
        self.config = config if config else get_config()
        self.session_id = session_id
        
        strategy_class = strategy_registry.get(strategy_name)
        if not strategy_class:
            raise ValueError(f"未找到名为 '{strategy_name}' 的策略")
        self.strategy: BaseStrategy = strategy_class(config=self.config)
        
        self.broker: AbstractBroker = self._initialize_broker()
        logger.info(f"交易引擎初始化完成，策略: {self.strategy.name}, 模式: {self.config.trading_mode}，经纪商: {self.config.trading_broker}，会话ID: {self.session_id}")

    def _initialize_broker(self) -> AbstractBroker:
        """
        根据配置初始化并返回相应的经纪商实例。
        """
        trading_mode = self.config.trading_mode
        # trading_broker 现在表示经纪商的“概念”类型 (paper, real_api, real_ui_automation)
        broker_concept_type = self.config.trading_broker
        # real_broker_type 表示具体的真实经纪商 (例如 guosen, tiger, ths_web)
        real_broker_type = self.config.real_broker_type

        if trading_mode == 'paper':
            return PaperBroker(session=self.db_session, session_id=self.session_id)
        elif trading_mode == 'live':
            # 尝试连接经纪商
            broker_instance = None
            if broker_concept_type == 'real_api':
                logger.info(f"尝试初始化真实 API 经纪商: {real_broker_type}...")
                # TODO: 在此处导入并实例化具体的 RealApiBroker(s)
                # 例如：from trading.brokers.guosen_api_broker import GuosenApiBroker
                if real_broker_type == 'guosen':
                    # broker_instance = GuosenApiBroker(config=self.config)
                    raise NotImplementedError(f"真实 API 经纪商 '{real_broker_type}' 尚未实现。")
                elif real_broker_type == 'tiger':
                    # broker_instance = TigerApiBroker(config=self.config)
                    raise NotImplementedError(f"真实 API 经纪商 '{real_broker_type}' 尚未实现。")
                else:
                    logger.error(f"不支持的真实 API 经纪商类型: '{real_broker_type}'")
                    raise ValueError(f"不支持的真实 API 经纪商类型: '{real_broker_type}'")
            elif broker_concept_type == 'real_ui_automation':
                logger.info(f"尝试初始化真实 UI 自动化经纪商: {real_broker_type}...")
                # TODO: 在此处导入并实例化具体的 UiAutomationBroker(s)
                # 例如：from trading.brokers.ths_web_ui_broker import ThsWebUiAutomationBroker
                if real_broker_type == 'ths_web':
                    # broker_instance = ThsWebUiAutomationBroker(config=self.config)
                    raise NotImplementedError(f"真实 UI 自动化经纪商 '{real_broker_type}' 尚未实现。")
                else:
                    logger.error(f"不支持的真实 UI 自动化经纪商类型: '{real_broker_type}'")
                    raise ValueError(f"不支持的真实 UI 自动化经纪商类型: '{real_broker_type}'")
            else:
                logger.error(f"在实盘模式下，不支持的经纪商概念类型: '{broker_concept_type}'。请配置 'real_api' 或 'real_ui_automation'。")
                raise ValueError(f"在实盘模式下，不支持的经纪商概念类型: '{broker_concept_type}'。请配置 'real_api' 或 'real_ui_automation'。")

            # 建立连接
            if broker_instance:
                logger.info(f"正在连接真实经纪商: {real_broker_type}...")
                try:
                    if broker_instance.connect(
                        api_key=self.config.real_broker_api_key,
                        api_secret=self.config.real_broker_api_secret,
                        account=self.config.real_broker_account,
                        password=self.config.real_broker_password,
                        browser_type=self.config.ui_automation_browser,
                        headless=self.config.ui_automation_headless
                    ):
                        logger.info(f"成功连接真实经纪商: {real_broker_type}")
                        return broker_instance
                    else:
                        logger.error(f"连接真实经纪商失败: {real_broker_type} - 连接方法返回 False。")
                        raise ConnectionError(f"无法连接到真实经纪商: {real_broker_type}")
                except Exception as e:
                    logger.error(f"连接真实经纪商 '{real_broker_type}' 时发生异常: {e}", exc_info=True)
                    raise ConnectionError(f"连接真实经纪商 '{real_broker_type}' 时发生异常: {e}") from e
            else:
                logger.error("经纪商实例未成功创建，无法进行连接。")
                raise RuntimeError("经纪商实例未成功创建。")
        else:
            logger.error(f"不支持的交易模式: '{trading_mode}'。")
            raise ValueError(f"不支持的交易模式: '{trading_mode}'。")

    def process_analysis(self, 
                         stock_code: str, 
                         analysis_result: Dict[str, Any], 
                         current_price: float,
                         trade_time: Optional[datetime] = None # 用于回测时传递模拟时间
                         ) -> Optional[str]:
        """
        处理单只股票的分析结果，并根据策略执行交易决策。

        Args:
            stock_code (str): 股票代码。
            analysis_result (Dict[str, Any]): 来自 Agent 的分析结果，例如 {'recommendation': 'BUY', ...}。
            current_price (float): 当前股票价格。
            trade_time (Optional[datetime]): 交易发生的时间，回测时提供。

        Returns:
            Optional[str]: 如果发生交易，返回订单ID，否则返回 None。
        """
        if not analysis_result:
            logger.warning(f"跳过 {stock_code}，因为分析结果为空。")
            return None

        # 在回测模式下，更新持仓的最新价格以计算市值
        if self.config.trading_mode == 'backtest':
            if isinstance(self.broker, PaperBroker): # 回测模式目前只支持 PaperBroker
                self.broker._update_position_current_price(stock_code, current_price)
            else:
                logger.warning("非 PaperBroker 无法在回测模式下更新持仓价格。")


        account_balance = self.broker.get_account_balance()
        current_positions = self.broker.list_positions()

        order_id = None
        try:
            # 尝试卖出
            if self.strategy.should_sell(stock_code, analysis_result, current_positions, account_balance, current_price):
                sell_quantity = self.strategy.get_sell_quantity(stock_code, current_positions)
                if sell_quantity > 0:
                    # 注意：实盘交易中，place_order 可能不会立即返回最终状态，order_id 仅代表订单提交成功。
                    # 实际订单状态和成交结果需要通过异步查询或回调机制更新。
                    order = self.broker.place_order(stock_code, 'SELL', sell_quantity, 'MARKET', current_price)
                    order_id = order.order_id
                    logger.info(f"交易引擎: {stock_code} 执行卖出 {sell_quantity} 股，订单ID: {order_id}")

            # 尝试买入 (卖出后可能还有资金)
            elif self.strategy.should_buy(stock_code, analysis_result, current_positions, account_balance, current_price):
                buy_quantity = self.strategy.get_buy_quantity(stock_code, current_price, account_balance)
                if buy_quantity > 0:
                    # 注意：实盘交易中，place_order 可能不会立即返回最终状态，order_id 仅代表订单提交成功。
                    # 实际订单状态和成交结果需要通过异步查询或回调机制更新。
                    order = self.broker.place_order(stock_code, 'BUY', buy_quantity, 'MARKET', current_price)
                    order_id = order.order_id
                    logger.info(f"交易引擎: {stock_code} 执行买入 {buy_quantity} 股，订单ID: {order_id}")
            
            # TODO: 实盘模式下，这里的 commit 可能需要更精细的控制，
            # 例如在收到订单成交回报后再更新数据库，而不是在提交订单后立即提交。
            self.db_session.commit()

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"处理 {stock_code} 交易决策时发生错误: {e}")

        return order_id

    def get_current_status(self) -> Dict[str, Any]:
        """
        获取当前交易引擎的模拟账户和持仓状态。
        """
        account_balance = self.broker.get_account_balance()
        positions = self.broker.list_positions()
        
        return {
            "account_balance": account_balance.to_dict(),
            "positions": [p.to_dict() for p in positions]
        }

    def place_manual_order(self, stock_code: str, direction: str, quantity: int, order_type: str, price: Optional[float] = None) -> Optional[str]:
        """
        Manually place an order.
        """
        try:
            # 注意：实盘交易中，place_order 可能不会立即返回最终状态，order_id 仅代表订单提交成功。
            # 实际订单状态和成交结果需要通过异步查询或回调机制更新。
            order = self.broker.place_order(stock_code, direction.upper(), quantity, order_type.upper(), price)
            # TODO: 实盘模式下，这里的 commit 可能需要更精细的控制，
            # 例如在收到订单成交回报后再更新数据库，而不是在提交订单后立即提交。
            self.db_session.commit()
            return order.order_id
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"手动下单失败: {e}")
            return None

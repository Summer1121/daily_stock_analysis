import logging
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from config import Config, get_config
from storage import DatabaseManager
from trading.brokers.base import AbstractBroker
from trading.brokers.paper_broker import PaperBroker # 暂时只使用 PaperBroker
from trading.strategy import TradingStrategy
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
                 session_id: str = "default_paper_session"
                 ):
        """
        初始化交易引擎。

        Args:
            db_session (Session): SQLAlchemy 数据库会话。
            config (Optional[Config]): 配置实例，如果未提供则从全局获取。
            session_id (str): 模拟或回测会话ID，用于隔离数据。
        """
        self.db_session = db_session
        self.config = config if config else get_config()
        self.session_id = session_id
        
        self.strategy = TradingStrategy(self.config)
        self.broker: AbstractBroker = self._initialize_broker()
        logger.info(f"交易引擎初始化完成，模式: {self.config.trading_mode}，经纪商: {self.config.trading_broker}，会话ID: {self.session_id}")

    def _initialize_broker(self) -> AbstractBroker:
        """
        根据配置初始化并返回相应的经纪商实例。
        """
        broker_type = self.config.trading_broker
        
        if broker_type == 'paper':
            # 在回测或模拟模式下，总是使用 PaperBroker
            return PaperBroker(session=self.db_session, session_id=self.session_id)
        elif self.config.trading_mode == 'live':
            # TODO: 实现真实的经纪商适配器
            raise NotImplementedError(f"真实经纪商 '{broker_type}' 尚未实现。")
        else:
            raise ValueError(f"不支持的经纪商类型或交易模式: {broker_type} / {self.config.trading_mode}")

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
                    order = self.broker.place_order(stock_code, 'SELL', sell_quantity, 'MARKET', current_price)
                    order_id = order.order_id
                    logger.info(f"交易引擎: {stock_code} 执行卖出 {sell_quantity} 股，订单ID: {order_id}")

            # 尝试买入 (卖出后可能还有资金)
            elif self.strategy.should_buy(stock_code, analysis_result, current_positions, account_balance, current_price):
                buy_quantity = self.strategy.get_buy_quantity(stock_code, current_price, account_balance)
                if buy_quantity > 0:
                    order = self.broker.place_order(stock_code, 'BUY', buy_quantity, 'MARKET', current_price)
                    order_id = order.order_id
                    logger.info(f"交易引擎: {stock_code} 执行买入 {buy_quantity} 股，订单ID: {order_id}")
            
            # 提交会话更改
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

from abc import ABC, abstractmethod
from typing import List, Optional

# 从 trading.models 导入我们定义的模型
from trading.models import Order, Position, AccountBalance, Trade

class AbstractBroker(ABC):
    """
    抽象经纪商接口 (Abstract Broker Interface)

    定义了与交易经纪商进行交互的标准方法。
    所有具体的经纪商实现（如 PaperBroker, RealBroker）都必须继承此抽象类。
    """

    @abstractmethod
    def get_account_balance(self) -> AccountBalance:
        """
        获取当前账户的资金余额信息。

        Returns:
            AccountBalance: 包含总资产、可用现金、持仓市值等信息的对象。
        """
        pass

    @abstractmethod
    def list_positions(self) -> List[Position]:
        """
        获取当前持仓列表。

        Returns:
            List[Position]: 当前所有持仓的列表。
        """
        pass

    @abstractmethod
    def get_position(self, stock_code: str) -> Optional[Position]:
        """
        获取指定股票的持仓信息。

        Args:
            stock_code (str): 股票代码。

        Returns:
            Optional[Position]: 指定股票的持仓信息，如果无持仓则返回 None。
        """
        pass

    @abstractmethod
    def place_order(self, stock_code: str, direction: str, quantity: int, order_type: str, price: Optional[float] = None) -> Order:
        """
        提交交易订单。

        Args:
            stock_code (str): 股票代码。
            direction (str): 交易方向 ('BUY' 或 'SELL')。
            quantity (int): 交易数量。
            order_type (str): 订单类型 ('MARKET' 或 'LIMIT')。
            price (Optional[float]): 限价单的指定价格，市价单可忽略。

        Returns:
            Order: 提交成功后的订单对象，包含订单ID和当前状态。
        """
        pass

    @abstractmethod
    def get_order(self, order_id: str) -> Optional[Order]:
        """
        查询指定订单的当前状态。

        Args:
            order_id (str): 订单ID。

        Returns:
            Optional[Order]: 订单对象，包含最新状态，如果订单不存在则返回 None。
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        尝试取消指定订单。

        Args:
            order_id (str): 订单ID。

        Returns:
            bool: 如果订单成功提交取消请求则返回 True，否则返回 False。
        """
        pass

    @abstractmethod
    def get_trades_by_order(self, order_id: str) -> List[Trade]:
        """
        获取指定订单的所有成交记录。

        Args:
            order_id (str): 订单ID。

        Returns:
            List[Trade]: 与该订单相关的所有成交记录。
        """
        pass

    @abstractmethod
    def connect(self, **kwargs) -> bool:
        """
        建立与交易经纪商的连接。
        不同的经纪商可能需要不同的连接参数（如API密钥、会话令牌等）。

        Returns:
            bool: 如果连接成功则返回 True，否则返回 False。
        """
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """
        断开与交易经纪商的连接。

        Returns:
            bool: 如果断开成功则返回 True，否则返回 False。
        """
        pass

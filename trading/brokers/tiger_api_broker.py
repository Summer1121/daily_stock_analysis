import logging
from typing import List, Optional, Any, Dict
from datetime import datetime

from tigeropen.common.consts import (
    Market, BarPeriod, OrderType, OrderStatus, TradeDirection,
    SecurityType, Currency, MarketState
)
from tigeropen.tiger_open_client import TigerOpenClient
from tigeropen.trade.trade_client import TradeClient
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.common.util.signature_utils import read_private_key
from tigeropen.tiger_open_config import TigerOpenClientConfig

from config import Config
from trading.brokers.base import AbstractBroker
from trading.models import Order, Position, AccountBalance, Trade

logger = logging.getLogger(__name__)

class TigerApiBroker(AbstractBroker):
    """
    老虎证券 API 经纪商实现

    通过 TigerOpen Python SDK 对接老虎证券的量化交易接口。
    """

    def __init__(self, config: Config):
        self.config = config
        self.client_config = TigerOpenClientConfig()
        self.client = None
        self.trade_client = None
        self.quote_client = None
        self._connected = False

    def connect(self, **kwargs) -> bool:
        """
        连接到老虎证券 API。

        Args:
            kwargs: 包含连接参数，如 `api_key` (Tiger ID), `api_secret` (私钥文件路径), `account`。
        """
        tiger_id = kwargs.get('api_key') or self.config.real_broker_api_key
        private_key_path = kwargs.get('api_secret') or self.config.real_broker_api_secret
        account = kwargs.get('account') or self.config.real_broker_account

        if not all([tiger_id, private_key_path, account]):
            logger.error("老虎证券 API 连接参数不完整：需要 Tiger ID, 私钥文件路径和账户号码。")
            return False

        try:
            self.client_config.private_key = read_private_key(private_key_path)
            self.client_config.tiger_id = tiger_id
            self.client_config.account = account
            # 可以根据需要配置服务器地址，默认是实盘环境
            # self.client_config.language = Language.zh_CN

            self.client = TigerOpenClient(self.client_config)
            self.trade_client = TradeClient(self.client)
            self.quote_client = QuoteClient(self.client)

            # 验证连接 - 尝试获取账户概要信息
            self.get_account_balance() # 尝试获取余额，如果失败则抛异常

            self._connected = True
            logger.info(f"成功连接到老虎证券 API，账户: {account}")
            return True
        except Exception as e:
            logger.error(f"连接老虎证券 API 失败: {e}", exc_info=True)
            self._connected = False
            return False

    def disconnect(self) -> bool:
        """
        断开与老虎证券 API 的连接。
        对于 TigerOpen SDK，通常没有显式的断开方法，只需清除客户端实例。
        """
        if self._connected:
            self.client = None
            self.trade_client = None
            self.quote_client = None
            self._connected = False
            logger.info("已断开与老虎证券 API 的连接。")
        return True

    def _check_connection(self):
        if not self._connected or self.trade_client is None or self.quote_client is None:
            raise ConnectionError("未连接到老虎证券 API 或客户端未初始化。请先调用 connect 方法。")

    def get_account_balance(self) -> AccountBalance:
        """
        获取当前账户的资金余额信息。
        """
        self._check_connection()
        try:
            # 获取所有账户概要，选择当前配置的账户
            accounts = self.trade_client.get_account_details()
            target_account = None
            for acc in accounts:
                if acc.account == self.client_config.account:
                    target_account = acc
                    break
            
            if not target_account:
                raise ValueError(f"未找到账户: {self.client_config.account}")

            # TigerOpen 的 Account 对象包含总资产、可用现金等信息
            # 这里的字段映射需要根据 TigerOpen SDK 实际返回的对象属性来调整
            # 假设 available_cash 对应 cash_balance, total_assets 对应 net_asset
            return AccountBalance(
                total_assets=target_account.net_asset,
                available_cash=target_account.cash_balance, # 可能需要区分货币类型
                market_value=target_account.market_value,
                frozen_cash=target_account.frozen_cash,
                currency=target_account.currency # 老虎证券通常支持多币种，此处简化
            )
        except Exception as e:
            logger.error(f"获取老虎证券账户余额失败: {e}", exc_info=True)
            raise

    def list_positions(self) -> List[Position]:
        """
        获取当前持仓列表。
        """
        self._check_connection()
        try:
            tiger_positions = self.trade_client.get_positions()
            positions = []
            for tp in tiger_positions:
                # 需要将 TigerOpen 的持仓对象转换为系统内部的 Position 模型
                positions.append(Position(
                    stock_code=tp.symbol, # TigerOpen 返回的 symbol 可能是 'AAPL'
                    quantity=tp.quantity,
                    cost_price=tp.average_cost,
                    current_price=tp.market_price, # 需要实时行情数据，或者从quote_client获取
                    market_value=tp.market_value # 或 quantity * market_price
                    # created_at, updated_at 需要额外逻辑处理
                ))
            return positions
        except Exception as e:
            logger.error(f"获取老虎证券持仓列表失败: {e}", exc_info=True)
            raise

    def get_position(self, stock_code: str) -> Optional[Position]:
        """
        获取指定股票的持仓信息。
        """
        # 可以优化为直接调用API查询单只股票持仓，但多数API是获取全部后过滤
        all_positions = self.list_positions()
        for pos in all_positions:
            if pos.stock_code == stock_code:
                return pos
        return None

    def place_order(self, stock_code: str, direction: str, quantity: int, order_type: str, price: Optional[float] = None) -> Order:
        """
        提交交易订单。
        """
        self._check_connection()
        try:
            # 映射系统订单类型和方向到 TigerOpen SDK
            tiger_direction = TradeDirection.BUY if direction.upper() == 'BUY' else TradeDirection.SELL
            
            if order_type.upper() == 'MARKET':
                tiger_order_type = OrderType.MKT
            elif order_type.upper() == 'LIMIT':
                tiger_order_type = OrderType.LMT
                if price is None:
                    raise ValueError("限价单 (LIMIT) 必须提供价格 (price)。")
            else:
                raise ValueError(f"不支持的订单类型: {order_type}")

            # 构建订单请求
            # symbol 需要根据市场调整，例如 US:AAPL, HK:00700
            # 这里简化处理，假设 stock_code 已经是 TigerOpen 接受的格式
            # 需要根据实际情况判断股票市场 (美股、港股等)
            
            # TODO: 确定股票市场，例如通过 stock_code 前缀或查询
            market = Market.US # 示例，实际需要动态判断
            
            # 使用 TradeClient 下单
            # order_id 返回的是 TigerOpen 的唯一订单号
            tiger_order = self.trade_client.place_order(
                account=self.client_config.account,
                symbol=stock_code,
                sec_type=SecurityType.STK, # 股票
                market=market,
                currency=Currency.USD, # 需要根据市场和股票动态设置
                action=tiger_direction,
                order_type=tiger_order_type,
                total_quantity=quantity,
                limit_price=price if tiger_order_type == OrderType.LMT else None,
                # 其他参数如 stop_price, time_in_force 等可以根据需求扩展
            )
            
            if tiger_order and tiger_order.order_id:
                # 返回系统内部的 Order 模型
                # 初始状态设为 NEW，后续通过 get_order 更新
                return Order(
                    order_id=str(tiger_order.order_id), # TigerOpen order_id 通常是数字
                    stock_code=stock_code,
                    order_type=order_type,
                    direction=direction,
                    quantity=quantity,
                    price=price,
                    status=OrderStatus.NEW.value # 初始状态
                )
            else:
                raise RuntimeError("老虎证券下单失败，未返回订单ID。")

        except Exception as e:
            logger.error(f"老虎证券下单失败: {e}", exc_info=True)
            raise

    def get_order(self, order_id: str) -> Optional[Order]:
        """
        查询指定订单的当前状态。
        """
        self._check_connection()
        try:
            # 查询单个订单详情
            tiger_orders = self.trade_client.get_orders(account=self.client_config.account, tiger_ids=[int(order_id)])
            if not tiger_orders:
                return None
            
            tiger_order = tiger_orders[0]
            # 映射 TigerOpen 订单状态到系统内部状态
            status_map = {
                OrderStatus.NEW: 'PENDING',
                OrderStatus.FILLED: 'FILLED',
                OrderStatus.PARTIALLY_FILLED: 'PARTIALLY_FILLED',
                OrderStatus.CANCELED: 'CANCELED',
                OrderStatus.PENDING_CANCEL: 'PENDING_CANCEL',
                OrderStatus.REJECTED: 'FAILED',
                OrderStatus.HELD: 'PENDING', # 待处理
                # ... 其他状态映射
            }
            system_status = status_map.get(tiger_order.status, 'UNKNOWN')

            # 需要从 TigerOpen 订单对象中获取成交均价、成交数量等
            executed_price = tiger_order.avg_fill_price if tiger_order.avg_fill_price else tiger_order.limit_price
            executed_quantity = tiger_order.filled_quantity if tiger_order.filled_quantity else 0

            return Order(
                order_id=str(tiger_order.order_id),
                stock_code=tiger_order.symbol,
                order_type=tiger_order.order_type.name, # MKT, LMT
                direction=tiger_order.action.name, # BUY, SELL
                quantity=tiger_order.total_quantity,
                price=executed_price, # 这里的 price 可能是限价或成交均价
                status=system_status,
                # created_at, updated_at 需要从 tiger_order 中解析
            )
        except Exception as e:
            logger.error(f"查询老虎证券订单 {order_id} 状态失败: {e}", exc_info=True)
            raise

    def cancel_order(self, order_id: str) -> bool:
        """
        尝试取消指定订单。
        """
        self._check_connection()
        try:
            cancel_result = self.trade_client.cancel_order(account=self.client_config.account, tiger_id=int(order_id))
            if cancel_result and cancel_result.is_success:
                logger.info(f"成功提交老虎证券订单 {order_id} 取消请求。")
                return True
            else:
                logger.warning(f"老虎证券订单 {order_id} 取消失败或未成功: {cancel_result.message if cancel_result else '未知错误'}")
                return False
        except Exception as e:
            logger.error(f"取消老虎证券订单 {order_id} 失败: {e}", exc_info=True)
            raise

    def get_trades_by_order(self, order_id: str) -> List[Trade]:
        """
        获取指定订单的所有成交记录。
        TigerOpen SDK 提供 get_order_transactions 来获取订单的成交明细。
        """
        self._check_connection()
        try:
            tiger_transactions = self.trade_client.get_order_transactions(account=self.client_config.account, tiger_id=int(order_id))
            trades = []
            for tt in tiger_transactions:
                # 将 TigerOpen 成交对象映射到系统内部 Trade 模型
                # TigerOpen 的成交对象通常包含费用信息
                trades.append(Trade(
                    order_id=order_id,
                    trade_id=str(tt.trade_id),
                    stock_code=tt.symbol,
                    direction=tt.action.name,
                    quantity=tt.filled_quantity,
                    price=tt.price,
                    amount=tt.amount, # 成交总金额
                    commission=tt.commission, # 佣金
                    stamp_duty=0.0, # 老虎证券可能没有明确的印花税字段，需要根据规则计算或默认为0
                    other_fees=tt.fees - tt.commission if tt.fees else 0.0, # 其他费用
                    net_amount=tt.amount - tt.commission - (tt.fees - tt.commission if tt.fees else 0.0) if tt.action == TradeDirection.BUY else tt.amount + tt.commission + (tt.fees - tt.commission if tt.fees else 0.0), # 简化计算，需要根据实际费率和方向调整
                    trade_time=datetime.fromtimestamp(tt.trade_time / 1000) # 毫秒转秒
                ))
            return trades
        except Exception as e:
            logger.error(f"获取老虎证券订单 {order_id} 成交记录失败: {e}", exc_info=True)
            raise

import uuid
import logging
from datetime import datetime
from typing import List, Optional, Union

from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from config import get_config
from trading.brokers.base import AbstractBroker
from trading.models import Order, Position, Trade, AccountBalance, PaperAccount

logger = logging.getLogger(__name__)

class PaperBroker(AbstractBroker):
    """
    模拟经纪商实现 (Paper Broker Implementation)

    继承自 AbstractBroker，所有操作都基于本地数据库进行模拟。
    适用于模拟交易和历史回测。
    """

    def __init__(self, session: Session, session_id: str = "default_paper_session"):
        """
        初始化 PaperBroker。

        Args:
            session (Session): SQLAlchemy 数据库会话。
            session_id (str): 模拟交易会话的唯一ID，用于区分不同的模拟账户。
        """
        self.session = session
        self.session_id = session_id
        self.config = get_config()
        self._initialize_account()

    def _initialize_account(self):
        """
        初始化或加载模拟账户。
        如果指定 session_id 的账户不存在，则创建一个新账户并注入初始资金。
        """
        paper_account = self.session.execute(
            select(PaperAccount).filter_by(session_id=self.session_id)
        ).scalar_one_or_none()

        if not paper_account:
            initial_capital = self.config.trading_capital
            paper_account = PaperAccount(
                session_id=self.session_id,
                initial_capital=initial_capital,
                available_cash=initial_capital,
                total_assets=initial_capital,
            )
            self.session.add(paper_account)
            self.session.commit()
            logger.info(f"模拟账户 {self.session_id} 初始化成功，初始资金: {initial_capital}")
        else:
            logger.info(f"模拟账户 {self.session_id} 加载成功，当前可用资金: {paper_account.available_cash}")

    def _get_paper_account(self) -> PaperAccount:
        """获取当前模拟账户实例"""
        account = self.session.execute(
            select(PaperAccount).filter_by(session_id=self.session_id)
        ).scalar_one_or_none()
        if not account:
            # 这不应该发生，因为初始化时会创建
            raise RuntimeError(f"模拟账户 {self.session_id} 不存在。")
        return account

    def get_account_balance(self) -> AccountBalance:
        """
        获取当前模拟账户的资金余额信息。
        需要更新持仓的市值以计算总资产。
        """
        account = self._get_paper_account()
        
        # 计算持仓市值
        total_market_value = 0.0
        positions = self.list_positions()
        for pos in positions:
            # 注意: 这里假设 Position.current_price 已由外部机制更新
            # 回测时，current_price 会来自当日收盘价
            # 实时模拟时，需要实时行情更新
            total_market_value += pos.quantity * pos.current_price

        account.market_value = total_market_value # 实时更新账户市值
        account.total_assets = account.available_cash + account.frozen_cash + total_market_value
        self.session.add(account)
        self.session.commit() # 保存更新

        return AccountBalance(
            total_assets=account.total_assets,
            available_cash=account.available_cash,
            market_value=total_market_value,
            frozen_cash=account.frozen_cash,
            currency="CNY"
        )

    def list_positions(self) -> List[Position]:
        """
        获取当前模拟账户的所有持仓列表。
        """
        positions = self.session.execute(
            select(Position).filter_by(session_id=self.session_id)
        ).scalars().all()
        return list(positions)

    def get_position(self, stock_code: str) -> Optional[Position]:
        """
        获取指定股票的持仓信息。
        """
        position = self.session.execute(
            select(Position)
            .filter_by(session_id=self.session_id, stock_code=stock_code)
        ).scalar_one_or_none()
        return position

    def place_order(self, stock_code: str, direction: str, quantity: int, order_type: str, price: Optional[float] = None) -> Order:
        """
        提交模拟交易订单。
        对于市价单，假设立即以指定价格成交。限价单也简化处理。
        """
        account = self._get_paper_account()
        order_uuid = str(uuid.uuid4())
        executed_price = price # 假设限价单价格或市价单的指定价格即为成交价

        # 确保价格有效，尤其对于市价单，需要一个模拟成交价
        if executed_price is None:
            # TODO: 在回测或实时模拟中，这里需要从数据源获取当前价格作为市价单的成交价
            # 暂时用一个默认值或引发错误
            logger.warning(f"市价单 {stock_code} 无指定价格，无法模拟成交。")
            raise ValueError(f"Market order {stock_code} requires an execution price for simulation.")

        # 预检查
        if direction == 'BUY':
            cost = executed_price * quantity
            if account.available_cash < cost:
                logger.warning(f"模拟买入失败: 资金不足。可用资金: {account.available_cash}, 需要: {cost}")
                raise ValueError("Insufficient cash for BUY order.")
            account.available_cash -= cost # 冻结或直接扣除

        elif direction == 'SELL':
            position = self.get_position(stock_code)
            if not position or position.quantity < quantity:
                logger.warning(f"模拟卖出失败: 持仓不足。持有: {position.quantity if position else 0}, 卖出: {quantity}")
                raise ValueError("Insufficient position for SELL order.")
        else:
            raise ValueError("Invalid direction. Must be 'BUY' or 'SELL'.")

        # 创建订单记录 (假设订单立即成交)
        order = Order(
            order_id=order_uuid,
            stock_code=stock_code,
            order_type=order_type,
            direction=direction,
            quantity=quantity,
            price=executed_price, # 记录成交价格
            status='FILLED',
            session_id=self.session_id # 关联到模拟会话
        )
        self.session.add(order)
        self.session.flush() # 确保 order_id 生成

        # 创建成交记录
        trade_uuid = str(uuid.uuid4())
        trade_amount = executed_price * quantity
        trade = Trade(
            order_id=order.order_id,
            trade_id=trade_uuid,
            stock_code=stock_code,
            direction=direction,
            quantity=quantity,
            price=executed_price,
            amount=trade_amount,
            trade_time=datetime.now(), # 模拟成交时间
            session_id=self.session_id # 关联到模拟会话
        )
        self.session.add(trade)

        # 更新持仓和账户
        position = self.get_position(stock_code)
        if direction == 'BUY':
            if position:
                # 更新平均成本
                total_quantity = position.quantity + quantity
                total_cost = (position.quantity * position.cost_price) + (quantity * executed_price)
                position.cost_price = total_cost / total_quantity
                position.quantity = total_quantity
                position.current_price = executed_price # 假设成交价为最新价
                position.updated_at = datetime.now()
            else:
                position = Position(
                    session_id=self.session_id, # 关联到模拟会话
                    stock_code=stock_code,
                    quantity=quantity,
                    cost_price=executed_price,
                    current_price=executed_price,
                )
                self.session.add(position)
            account.total_assets += (quantity * executed_price) # 增加总资产

        elif direction == 'SELL':
            if position:
                position.quantity -= quantity
                if position.quantity == 0:
                    self.session.delete(position) # 清除持仓
                else:
                    position.updated_at = datetime.now()
            account.available_cash += trade_amount # 资金入账
            account.total_assets -= (quantity * executed_price) # 减少总资产

        self.session.add(account) # 保存账户变动

        self.session.commit()
        logger.info(f"模拟交易成功: {direction} {quantity} {stock_code} @ {executed_price}")
        return order

    def get_order(self, order_id: str) -> Optional[Order]:
        """
        查询指定模拟订单的当前状态。
        """
        order = self.session.execute(
            select(Order).filter_by(session_id=self.session_id, order_id=order_id)
        ).scalar_one_or_none()
        return order

    def cancel_order(self, order_id: str) -> bool:
        """
        尝试取消模拟订单。
        由于我们假设订单立即成交，所以取消操作通常会失败。
        未来可以实现PENDING状态的限价单取消逻辑。
        """
        order = self.session.execute(
            select(Order).filter_by(session_id=self.session_id, order_id=order_id)
        ).scalar_one_or_none()

        if order and order.status == 'PENDING':
            order.status = 'CANCELED'
            order.updated_at = datetime.now()
            # 如果订单有冻结资金，需要解冻
            # account = self._get_paper_account()
            # account.available_cash += (order.quantity * order.price) # 假设冻结金额
            # self.session.add(account)
            self.session.commit()
            logger.info(f"模拟订单 {order_id} 已取消。")
            return True
        elif order and order.status == 'FILLED':
            logger.warning(f"模拟订单 {order_id} 已成交，无法取消。")
            return False
        else:
            logger.warning(f"模拟订单 {order_id} 不存在或状态不支持取消。")
            return False

    def get_trades_by_order(self, order_id: str) -> List[Trade]:
        """
        获取指定模拟订单的所有成交记录。
        """
        trades = self.session.execute(
            select(Trade).filter_by(session_id=self.session_id, order_id=order_id)
        ).scalars().all()
        return list(trades)

    def _update_position_current_price(self, stock_code: str, current_price: float):
        """
        更新指定股票的持仓当前价格和市值。
        这个方法主要用于回测中更新每天的收盘价，或实时模拟中更新实时价格。
        """
        position = self.get_position(stock_code)
        if position:
            position.current_price = current_price
            position.market_value = position.quantity * current_price
            position.updated_at = datetime.now()
            self.session.add(position)
            # 账户总资产会在 get_account_balance 中重新计算并commit
            logger.debug(f"更新 {self.session_id} 持仓 {stock_code} 最新价: {current_price}")
            return True
        return False

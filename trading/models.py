from datetime import datetime
from typing import Dict, Any
from dataclasses import dataclass, field # 新增导入

from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    DateTime,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import declarative_base # This would be problematic if Base is already declarative_base from storage.py

# Assuming Base is declarative_base() from storage.py
# We need to import the actual Base instance from storage to ensure all models
# are registered with the same metadata for create_all to work correctly.
from storage import Base

class Order(Base):
    """
    订单模型
    """
    __tablename__ = 'trading_orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(64), nullable=False, unique=True, index=True) # 假设外部订单ID最长64位
    stock_code = Column(String(10), nullable=False, index=True)
    order_type = Column(String(20), nullable=False)  # e.g., 'MARKET', 'LIMIT'
    direction = Column(String(10), nullable=False)   # e.g., 'BUY', 'SELL'
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=True) # for limit order or executed price
    status = Column(String(20), nullable=False, default='PENDING', index=True) # e.g., 'PENDING', 'FILLED', 'CANCELED', 'FAILED'
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<Order(order_id={self.order_id}, stock_code={self.stock_code}, direction={self.direction}, quantity={self.quantity}, status={self.status})>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'order_id': self.order_id,
            'stock_code': self.stock_code,
            'order_type': self.order_type,
            'direction': self.direction,
            'quantity': self.quantity,
            'price': self.price,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class Position(Base):
    """
    持仓模型
    """
    __tablename__ = 'trading_positions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(10), nullable=False, unique=True, index=True) # 同一股票只能有一个持仓记录
    quantity = Column(Integer, nullable=False, default=0)
    cost_price = Column(Float, nullable=False, default=0.0) # 平均成本价
    current_price = Column(Float, nullable=False, default=0.0) # 最新市场价
    market_value = Column(Float, nullable=False, default=0.0) # 市值 = quantity * current_price
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<Position(stock_code={self.stock_code}, quantity={self.quantity}, cost_price={self.cost_price})>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'stock_code': self.stock_code,
            'quantity': self.quantity,
            'cost_price': self.cost_price,
            'current_price': self.current_price,
            'market_value': self.market_value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class Trade(Base):
    """
    成交记录模型
    """
    __tablename__ = 'trading_trades'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(64), nullable=False, index=True) # 关联的订单ID
    trade_id = Column(String(64), nullable=False, unique=True, index=True) # 交易系统或券商的唯一成交ID
    stock_code = Column(String(10), nullable=False, index=True)
    direction = Column(String(10), nullable=False) # 'BUY' or 'SELL'
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False) # 成交价格
    amount = Column(Float, nullable=False) # 成交金额 = quantity * price
    trade_time = Column(DateTime, nullable=False) # 实际成交时间
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Trade(trade_id={self.trade_id}, stock_code={self.stock_code}, direction={self.direction}, quantity={self.quantity}, price={self.price})>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'order_id': self.order_id,
            'trade_id': self.trade_id,
            'stock_code': self.stock_code,
            'direction': self.direction,
            'quantity': self.quantity,
            'price': self.price,
            'amount': self.amount,
            'trade_time': self.trade_time.isoformat() if self.trade_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @dataclass
class AccountBalance:
    """
    账户资金余额模型
    用于表示账户的资金状态，非ORM模型。
    """
    total_assets: float = 0.0      # 总资产
    available_cash: float = 0.0    # 可用现金
    market_value: float = 0.0      # 持仓市值
    frozen_cash: float = 0.0       # 冻结资金（下单未成交部分）
    currency: str = "CNY"          # 币种

class PaperAccount(Base):
    """
    模拟账户资金模型
    每个模拟交易会话（或总的模拟账户）只有一个记录
    """
    __tablename__ = 'trading_paper_account'

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 用于区分不同的模拟交易会话，例如回测会话ID或用户ID
    session_id = Column(String(64), nullable=False, unique=True, index=True)

    initial_capital = Column(Float, nullable=False) # 初始资金
    available_cash = Column(Float, nullable=False)  # 可用现金
    frozen_cash = Column(Float, nullable=False, default=0.0) # 冻结资金
    total_assets = Column(Float, nullable=False) # 总资产 (随持仓市值变化)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<PaperAccount(session_id={self.session_id}, available_cash={self.available_cash}, total_assets={self.total_assets})>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'session_id': self.session_id,
            'initial_capital': self.initial_capital,
            'available_cash': self.available_cash,
            'frozen_cash': self.frozen_cash,
            'total_assets': self.total_assets,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

from storage import get_db, DatabaseManager
from trading.models import Position, PaperAccount
from trading.strategy import strategy_registry
from trading.engine import TradingEngine

router = APIRouter()

# 在内存中简单存储策略状态
strategy_status: Dict[str, bool] = {name: True for name in strategy_registry.keys()}


class OrderRequest(BaseModel):
    stock_code: str
    direction: str
    quantity: int
    order_type: str = "MARKET"
    price: Optional[float] = None


@router.get("/dashboard")
def get_trading_dashboard(db: DatabaseManager = Depends(get_db)):
    """Get trading dashboard data (positions and account balance)"""
    with db.get_session() as session:
        positions = session.query(Position).all()
        # Assuming a single paper account for now
        paper_account = session.query(PaperAccount).first()

        return {
            "positions": [p.to_dict() for p in positions],
            "account_balance": paper_account.to_dict() if paper_account else None,
        }


@router.get("/strategies")
def get_strategies():
    """Get a list of available strategies and their status"""
    return [
        {"name": name, "enabled": strategy_status.get(name, False)}
        for name in strategy_registry.keys()
    ]


@router.post("/strategies/{strategy_name}/toggle")
def toggle_strategy(strategy_name: str):
    """Enable or disable a strategy"""
    if strategy_name not in strategy_registry:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # 在这个简单的实现中，我们只允许一个策略处于激活状态
    for name in strategy_status:
        strategy_status[name] = False
    strategy_status[strategy_name] = True

    # 更新配置中的当前策略
    # 注意：这会修改全局配置，需要更复杂的配置管理方案
    # from config import get_config
    # config = get_config()
    # config.active_strategy = strategy_name

    return {"message": f"Strategy {strategy_name} toggled", "status": strategy_status}


@router.post("/order")
def place_order(order_request: OrderRequest, db: DatabaseManager = Depends(get_db)):
    """Place a manual order"""
    with db.get_session() as session:
        # Assuming a single trading engine for now
        engine = TradingEngine(db_session=session)
        order_id = engine.place_manual_order(
            stock_code=order_request.stock_code,
            direction=order_request.direction,
            quantity=order_request.quantity,
            order_type=order_request.order_type,
            price=order_request.price,
        )
        if order_id:
            return {"message": "Order placed successfully", "order_id": order_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to place order")


class BacktestRequest(BaseModel):
    stock_codes: List[str]
    start_date: str
    end_date: str
    strategy_name: str


@router.post("/backtest")
def run_backtest(backtest_request: BacktestRequest):
    """Run a backtest"""
    from trading.backtester import Backtester
    from datetime import datetime

    backtester = Backtester()
    report = backtester.run(
        stock_codes=backtest_request.stock_codes,
        start_date=datetime.strptime(backtest_request.start_date, "%Y-%m-%d").date(),
        end_date=datetime.strptime(backtest_request.end_date, "%Y-%m-%d").date(),
        strategy_name=backtest_request.strategy_name,
    )
    return report

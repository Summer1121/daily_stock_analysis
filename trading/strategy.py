import logging
from typing import Dict, Any, List, Optional, Type
from abc import ABC, abstractmethod

from config import Config, get_config
from trading.models import Position, AccountBalance

logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    """交易策略基类"""

    def __init__(self, config: Optional[Config] = None, **kwargs):
        self.config = config or get_config()
        self.name = self.__class__.__name__

    @abstractmethod
    def should_buy(self, stock_code: str, analysis_result: Dict[str, Any], current_positions: List[Position], account_balance: AccountBalance, current_price: float) -> bool:
        pass

    @abstractmethod
    def should_sell(self, stock_code: str, analysis_result: Dict[str, Any], current_positions: List[Position], account_balance: AccountBalance, current_price: float) -> bool:
        pass

    def get_buy_quantity(self, stock_code: str, current_price: float, account_balance: AccountBalance) -> int:
        if current_price <= 0:
            return 0
        
        max_possible_qty = int((account_balance.available_cash / current_price) // 100) * 100
        if max_possible_qty <= 0:
            return 0

        max_qty_by_position_limit = int((self.config.trading_max_position_per_stock / current_price) // 100) * 100
        if max_qty_by_position_limit <= 0:
             max_qty_by_position_limit = 100

        buy_qty = min(max_possible_qty, max_qty_by_position_limit)
        return max(0, (buy_qty // 100) * 100)

    def get_sell_quantity(self, stock_code: str, current_positions: List[Position]) -> int:
        existing_position = next((p for p in current_positions if p.stock_code == stock_code), None)
        if not existing_position or existing_position.quantity <= 0:
            return 0
        return (existing_position.quantity // 100) * 100


class FollowLLMStrategy(BaseStrategy):
    """跟随 LLM 分析结果的策略"""

    def should_buy(self, stock_code: str, analysis_result: Dict[str, Any], current_positions: List[Position], account_balance: AccountBalance, current_price: float) -> bool:
        recommendation = analysis_result.get('operation_advice')
        if recommendation not in ['买入', '加仓', '强烈买入']:
            return False

        existing_position = next((p for p in current_positions if p.stock_code == stock_code), None)
        if existing_position and existing_position.quantity > 0:
            logger.debug(f"策略: {stock_code} 已有持仓，不重复买入。")
            return False

        min_buy_quantity = 100
        estimated_cost = current_price * min_buy_quantity
        if estimated_cost > account_balance.available_cash:
            logger.debug(f"策略: {stock_code} 资金不足购买 {min_buy_quantity} 股。")
            return False
        
        if (existing_position.market_value if existing_position else 0) + estimated_cost > self.config.trading_max_position_per_stock:
            logger.debug(f"策略: {stock_code} 购买后将超出单股持仓金额上限")
            return False

        logger.info(f"策略: {stock_code} 满足买入条件。")
        return True

    def should_sell(self, stock_code: str, analysis_result: Dict[str, Any], current_positions: List[Position], account_balance: AccountBalance, current_price: float) -> bool:
        recommendation = analysis_result.get('operation_advice')
        if recommendation not in ['卖出', '减仓', '强烈卖出']:
            return False

        existing_position = next((p for p in current_positions if p.stock_code == stock_code), None)
        if not existing_position or existing_position.quantity <= 0:
            logger.debug(f"策略: {stock_code} 未持有或持仓为0，不执行卖出。")
            return False

        logger.info(f"策略: {stock_code} 满足卖出条件。")
        return True


class BuyAndHoldStrategy(BaseStrategy):
    """买入并持有策略"""

    def should_buy(self, stock_code: str, analysis_result: Dict[str, Any], current_positions: List[Position], account_balance: AccountBalance, current_price: float) -> bool:
        # 只要有钱，就买入
        existing_position = next((p for p in current_positions if p.stock_code == stock_code), None)
        if existing_position and existing_position.quantity > 0:
            return False

        min_buy_quantity = 100
        estimated_cost = current_price * min_buy_quantity
        if estimated_cost > account_balance.available_cash:
            return False
        
        return True

    def should_sell(self, stock_code: str, analysis_result: Dict[str, Any], current_positions: List[Position], account_balance: AccountBalance, current_price: float) -> bool:
        # 永不卖出
        return False


# 策略注册表
strategy_registry: Dict[str, Type[BaseStrategy]] = {
    "FollowLLMStrategy": FollowLLMStrategy,
    "BuyAndHoldStrategy": BuyAndHoldStrategy,
}


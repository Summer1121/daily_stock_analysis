import logging
from typing import Dict, Any, List, Optional

from config import Config, get_config
from trading.models import Position, AccountBalance

logger = logging.getLogger(__name__)

class TradingStrategy:
    """
    交易策略类

    负责根据分析结果和用户配置，生成买卖决策。
    """

    def __init__(self, config: Optional[Config] = None):
        """
        初始化交易策略。

        Args:
            config (Optional[Config]): 配置实例，如果未提供则从全局获取。
        """
        self.config = config if config else get_config()
        self.max_position_per_stock = self.config.trading_max_position_per_stock
        logger.info(f"交易策略初始化完成。单股最大持仓金额: {self.max_position_per_stock}")

    def should_buy(self, 
                   stock_code: str,
                   analysis_result: Dict[str, Any], 
                   current_positions: List[Position],
                   account_balance: AccountBalance,
                   current_price: float # 方便计算
                   ) -> bool:
        """
        判断是否应该买入。

        Args:
            stock_code (str): 股票代码。
            analysis_result (Dict[str, Any]): 来自 LLM 的分析结果。
            current_positions (List[Position]): 当前所有持仓。
            account_balance (AccountBalance): 当前账户资金余额。
            current_price (float): 股票当前价格。

        Returns:
            bool: 如果应该买入则返回 True，否则返回 False。
        """
        recommendation = analysis_result.get('recommendation')
        if recommendation != 'BUY':
            return False

        # 检查是否已有持仓
        existing_position = next((p for p in current_positions if p.stock_code == stock_code), None)
        if existing_position and existing_position.quantity > 0:
            logger.debug(f"策略: {stock_code} 已有持仓，不重复买入。")
            return False
            # 扩展：可以考虑加仓逻辑，但V1简化为不重复买入

        # 检查资金是否足够购买至少100股 (A股最小交易单位)
        # TODO: 购买数量的确定逻辑需要更复杂，这里简化
        min_buy_quantity = 100
        estimated_cost = current_price * min_buy_quantity
        if estimated_cost > account_balance.available_cash:
            logger.debug(f"策略: {stock_code} 资金不足购买 {min_buy_quantity} 股。可用: {account_balance.available_cash}, 需: {estimated_cost}")
            return False
        
        # 检查单股持仓金额上限
        if (existing_position.market_value if existing_position else 0) + estimated_cost > self.max_position_per_stock:
            logger.debug(f"策略: {stock_code} 购买后将超出单股持仓金额上限 {self.max_position_per_stock}")
            return False

        logger.info(f"策略: {stock_code} 满足买入条件。")
        return True

    def should_sell(self, 
                    stock_code: str,
                    analysis_result: Dict[str, Any], 
                    current_positions: List[Position],
                    account_balance: AccountBalance,
                    current_price: float # 方便计算
                    ) -> bool:
        """
        判断是否应该卖出。

        Args:
            stock_code (str): 股票代码。
            analysis_result (Dict[str, Any]): 来自 LLM 的分析结果。
            current_positions (List[Position]): 当前所有持仓。
            account_balance (AccountBalance): 当前账户资金余额。
            current_price (float): 股票当前价格。

        Returns:
            bool: 如果应该卖出则返回 True，否则返回 False。
        """
        recommendation = analysis_result.get('recommendation')
        if recommendation != 'SELL':
            return False

        # 检查是否持有该股票
        existing_position = next((p for p in current_positions if p.stock_code == stock_code), None)
        if not existing_position or existing_position.quantity <= 0:
            logger.debug(f"策略: {stock_code} 未持有或持仓为0，不执行卖出。")
            return False
        
        # TODO: 更多卖出逻辑，例如止损价触发，目标价触发等
        # 目前简化为分析推荐卖出且持有就卖

        logger.info(f"策略: {stock_code} 满足卖出条件。")
        return True

    def get_buy_quantity(self, stock_code: str, current_price: float, account_balance: AccountBalance) -> int:
        """
        计算买入数量。

        Args:
            stock_code (str): 股票代码。
            current_price (float): 股票当前价格。
            account_balance (AccountBalance): 当前账户资金余额。

        Returns:
            int: 建议的买入数量（股），必须是100的整数倍。
        """
        if current_price <= 0:
            return 0
        
        # 可用资金最多能买多少股 (100股为单位)
        max_possible_qty = int((account_balance.available_cash / current_price) // 100) * 100
        if max_possible_qty <= 0:
            return 0

        # 根据单股最大持仓金额计算可以买多少股
        # 假设当前没有持仓，直接按上限买
        max_qty_by_position_limit = int((self.max_position_per_stock / current_price) // 100) * 100
        if max_qty_by_position_limit <= 0:
             max_qty_by_position_limit = 100 # 最少买100股

        buy_qty = min(max_possible_qty, max_qty_by_position_limit)
        
        # 确保买入数量是100的整数倍
        return max(0, (buy_qty // 100) * 100)

    def get_sell_quantity(self, stock_code: str, current_positions: List[Position]) -> int:
        """
        计算卖出数量。

        Args:
            stock_code (str): 股票代码。
            current_positions (List[Position]): 当前所有持仓。

        Returns:
            int: 建议的卖出数量（股），必须是100的整数倍。
        """
        existing_position = next((p for p in current_positions if p.stock_code == stock_code), None)
        if not existing_position or existing_position.quantity <= 0:
            return 0
        
        # 目前策略是全仓卖出
        return (existing_position.quantity // 100) * 100

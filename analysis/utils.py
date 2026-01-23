# -*- coding: utf-8 -*-
"""
===================================
A股自选股智能分析系统 - 分析工具函数
===================================

职责：
1. 提供股票名称映射。
2. 提供公共的格式化函数。
"""

from typing import Optional

# 股票名称映射（常见股票）
STOCK_NAME_MAP = {
    '600519': '贵州茅台',
    '000001': '平安银行',
    '300750': '宁德时代',
    '002594': '比亚迪',
    '600036': '招商银行',
    '601318': '中国平安',
    '000858': '五粮液',
    '600276': '恒瑞医药',
    '601012': '隆基绿能',
    '002475': '立讯精密',
    '300059': '东方财富',
    '002415': '海康威视',
    '600900': '长江电力',
    '601166': '兴业银行',
    '600028': '中国石化',
}

def format_volume(volume: Optional[float]) -> str:
    """格式化成交量显示"""
    if volume is None:
        return 'N/A'
    if volume >= 1e8:
        return f"{volume / 1e8:.2f} 亿股"
    elif volume >= 1e4:
        return f"{volume / 1e4:.2f} 万股"
    else:
        return f"{volume:.0f} 股"

def format_amount(amount: Optional[float]) -> str:
    """格式化成交额显示"""
    if amount is None:
        return 'N/A'
    if amount >= 1e8:
        return f"{amount / 1e8:.2f} 亿元"
    elif amount >= 1e4:
        return f"{amount / 1e4:.2f} 万元"
    else:
        return f"{amount:.0f} 元"

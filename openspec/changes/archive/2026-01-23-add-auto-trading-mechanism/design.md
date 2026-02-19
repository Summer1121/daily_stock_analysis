# Design: 自动交易机制架构设计

本设计文档旨在为“自动交易机制”提供一个健壮、可扩展且安全的架构方案，现已包含回测引擎和双层 LLM 架构。

## 1. 核心原则

-   **安全第一**: 架构必须能够最大限度地降低潜在的资金损失风险。默认启用模拟盘，真实交易需要用户多次确认。
-   **接口驱动**: 所有与外部券商的交互都必须通过一个统一的、抽象的接口进行，实现与具体券商的解耦。
-   **状态持久化**: 交易系统必须持久化所有关键状态（如持仓、订单、资金变动），以便于跟踪、审计和故障恢复。
-   **可回测性**: 所有策略和分析逻辑的设计都必须能够支持历史回测，不能包含“未来函数”。

## 2. 双层 LLM 协作架构 (Two-Tier LLM Architecture)

为了降低大模型的使用成本并提高效率，我们将原有的 `analyzer.py` 升级为 Agent 化的双层协作架构。

```
analysis/
├── __init__.py
├── orchestrator.py    # Agent 协调器
├── agents/
│   ├── __init__.py
│   ├── summarizer.py  # 摘要 Agent (小模型)
│   └── decision.py    # 决策 Agent (大模型)
└── prompts.py         # Prompt 模板
```

### 2.1. 工作流

**新流程**: `原始数据 -> Orchestrator -> SummarizerAgent -> DecisionAgent -> 交易引擎`

1.  **Orchestrator (协调器)**: 负责接收原始数据（如多篇新闻、市场公告），调用 `SummarizerAgent`。
2.  **SummarizerAgent (摘要 Agent)**:
    -   **模型**: 使用一个轻量级、低成本的模型（如 `gemini-3-flash-preview` 或本地 Ollama 模型）。
    -   **输入**: 大段的文本信息。
    -   **处理**: 将输入的多篇新闻或公告，根据预设的 Prompt (例如：“请从以下新闻中提取与‘XX股票’相关的要点，总结市场情绪是积极、消极还是中性”)，汇总成一段结构化的、精炼的文本摘要。
    -   **输出**: 格式化的摘要文本。
3.  **DecisionAgent (决策 Agent)**:
    -   **模型**: 使用核心的、能力更强的大模型（如 `gemini-1.5-pro-preview`）。
    -   **输入**: 来自 `SummarizerAgent` 的精炼摘要和核心的量价数据。
    -   **处理**: 做出最终的、带有买卖点位的决策仪表盘。

## 3. 交易与回测模块设计

我们将引入一个新的 `trading` 包来容纳所有与交易和回测相关的功能。

```
trading/
├── __init__.py
├── engine.py             # 交易决策与执行引擎
├── models.py             # 数据模型 (Order, Position, Trade)
├── brokers/              # 经纪商适配器
│   ├── __init__.py
│   ├── base.py           # AbstractBroker (抽象基类)
│   └── paper_broker.py   # 模拟经纪商实现
├── strategy.py           # 交易策略 (基于配置)
└── backtester.py         # 回测引擎
```

### 3.1. 回测引擎 (`trading.backtester`)

`Backtester` 是衡量策略有效性的核心工具。

-   **职责**:
    1.  **数据加载**: 根据指定的股票和时间段获取全部历史日线数据。
    2.  **时间旅行 (主循环)**: 按天循环历史数据, 在每个循环中，只将当日及之前的数据提供给分析和交易引擎，杜绝“未来函数”。
    3.  **绩效统计**: 循环结束后，生成一份详细的报告，包含总回报率、最大回撤、夏普比率等。
-   **关键挑战**:
    -   **历史新闻数据**: 获取与历史行情精确匹配的新闻数据非常困难。因此，**V1 版本的回测将主要针对基于量价数据的技术策略**。

### 3.2. 经纪商接口 (`trading.brokers`)

为了适应不同的券商 API，我们将定义一个抽象基类 `AbstractBroker`。

`trading/brokers/base.py`:
```python
from abc import ABC, abstractmethod
from typing import List, Optional
from trading.models import Order, Position, AccountBalance

class AbstractBroker(ABC):
    @abstractmethod
    def get_account_balance(self) -> AccountBalance:
        """获取账户余额"""
        pass

    @abstractmethod
    def list_positions(self) -> List[Position]:
        """获取当前持仓"""
        pass

    @abstractmethod
    def place_order(self, order: Order) -> Order:
        """提交订单"""
        pass

    @abstractmethod
    def get_order(self, order_id: str) -> Optional[Order]:
        """查询订单状态"""
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        pass
```
-   **`PaperBroker`**: `trading/brokers/paper_broker.py` 将是 `AbstractBroker` 的第一个实现。它不进行任何真实交易，所有操作仅在本地数据库中模拟，将作为系统的**默认经纪商**。

### 3.3. 数据模型 (`trading.models`)

我们将使用 SQLAlchemy 在现有数据库中创建新的表来持久化交易状态。

-   **`Position` (持仓)**: `stock_code`, `quantity`, `cost_price`, `current_price`, `market_value`
-   **`Order` (订单)**: `order_id`, `stock_code`, `order_type`, `direction`, `quantity`, `price`, `status`, `created_at`, `updated_at`
-   **`Trade` (成交记录)**: 记录每一笔实际发生的成交。

### 3.4. 交易策略 (`trading.strategy`)

`TradingStrategy` 类将封装用户的配置，并提供决策逻辑。

`trading/strategy.py`:
```python
class TradingStrategy:
    def __init__(self, config):
        self.max_capital = config.get("TRADING_MAX_CAPITAL")
        self.max_position_per_stock = config.get("TRADING_MAX_POSITION_PER_STOCK")
        # ... 其他配置

    def should_buy(self, analysis_result, current_positions) -> bool:
        # 决策逻辑...
        pass
```

### 3.5. 交易引擎 (`trading.engine`)

`TradingEngine` 是整个流程的协调器。
-   **职责扩展**: 新增一个运行模式的参数，使其可以在`模拟交易`、`实盘交易`和`回测`三种模式下工作。在`回测`模式下，它将与 `Backtester` 协同工作。

## 4. 安全性设计

-   **API 密钥管理**: 真实券商的 API Key/Secret 必须通过环境变量（如 `BROKER_API_KEY`）注入，并存储在 GitHub Secrets 中。程序和文档中必须反复强调其敏感性和风险。
-   **交易模式开关**: 引入一个全局配置 `TRADING_MODE`，可选值为 `paper` (默认) 和 `live`。只有当 `TRADING_MODE` 明确设置为 `live` 时，系统才会尝试加载真实的券商适配器。

## 5. 做空机制的探讨

-   **实现**: 做空（Short Selling）通常涉及“融券卖出”和“买券还券”两个操作。
-   **挑战**: 不同券商的 API 对融券业务的支持不同，接口复杂；做空风险极高。
-   **结论**: 在项目初期，**不建议实现做空功能**。应首先确保做多流程的稳定和安全。在未来，可以作为一个独立的、高风险的扩展功能来考虑。

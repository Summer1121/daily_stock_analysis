# Tasks: 自动交易机制实施清单

本清单将整个开发过程分解为一系列可管理的任务。任务按依赖关系排序。

## Phase 1: 核心框架与模拟交易 (Foundation & Paper Trading)

此阶段的目标是搭建一个功能完整的、但只在模拟环境中运行的交易系统。

- [x] **[数据模型]** 在 `storage.py` (或新的 `trading/models.py`) 中定义 `Order`, `Position`, `Trade` 三个 SQLAlchemy 模型，并更新数据库初始化逻辑以创建这些表。
- [x] **[配置]** 在 `config.py` 和 `.env.example` 中添加新的配置段 `[trading]`，包括 `TRADING_MODE`, `TRADING_BROKER`, `TRADING_CAPITAL` 等。
- [x] **[架构]** 创建 `trading/` 目录结构。
- [x] **[核心接口]** 在 `trading/brokers/base.py` 中定义 `AbstractBroker` 抽象基类。
- [x] **[模拟实现]** 在 `trading/brokers/paper_broker.py` 中实现 `PaperBroker` 类，使其所有操作都基于本地数据库。
- [x] **[策略逻辑]** 在 `trading/strategy.py` 中实现 `TradingStrategy` 类，用于加载交易配置并提供决策逻辑。
- [x] **[交易引擎]** 在 `trading/engine.py` 中实现 `TradingEngine` 类，使其能够根据策略和分析结果，通过 `PaperBroker` “执行”订单。
- [x] **[集成]** 修改 `main.py`，将分析结果传递给 `TradingEngine`。
- [x] **[测试]** 为 `PaperBroker` 和 `TradingStrategy` 编写单元测试。
- [x] **[文档]** 初步更新文档，说明模拟交易功能。

## Phase 1.5: 回测与分析优化 (Backtesting & Analysis Optimization) - [新]

此阶段的目标是在实盘前，对策略进行科学的验证，并优化分析流程的成本与效率。

-   **依赖关系**: 必须在 Phase 1 成功完成后才能开始。

- [x] **[LLM架构]** 将 `analyzer.py` 重构为新的 `analysis/` 包，包含 `agents/` 和 `orchestrator.py`。
- [x] **[LLM架构]** 在 `analysis/agents/summarizer.py` 中实现 `SummarizerAgent`，使用一个轻量级模型处理信息摘要。
- [x] **[LLM架构]** 在 `analysis/agents/decision.py` 中实现 `DecisionAgent`，专注于核心决策。
- [x] **[LLM架构]** 在 `analysis/orchestrator.py` 中实现工作流，负责协调两个 Agent。
- [x] **[配置]** 在 `.env.example` 中添加 `SUMMARIZER_MODEL_NAME` 等小模型相关的配置。
- [x] **[回测架构]** 在 `trading/backtester.py` 中创建 `Backtester` 类。
- [x] **[回测数据]** 在 `Backtester` 中实现历史数据加载和缓存功能。
- [x] **[回测核心]** 实现 `Backtester` 的主循环，确保以“时间旅行”模式按天调用分析和交易引擎，杜绝未来函数。
- [x] **[回测集成]** 修改 `TradingEngine` 以支持新的“回测”模式，在该模式下与 `Backtester` 协同工作。
- [x] **[回测报告]** 实现绩效统计功能，在回测结束后生成包含总回报、最大回撤、夏普比率的报告。
- [x] **[测试]** 编写一个完整的回测单元测试，使用一个简单的策略（如金叉买入）在一段已知的历史数据上运行，断言其结果符合预期。

## Phase 2: 真实交易集成与 WebUI (Live Trading & UI)

-   **依赖关系**: 必须在 Phase 1.5 成功完成后才能开始。
-   **警告**: 此阶段涉及真实资金风险。

- [x] **[真实经纪商]** (示例) 为一个真实券商实现具体的 `AbstractBroker` 适配器。
- [x] **[配置]** 在 `.env.example` 中添加 `BROKER_API_KEY`, `BROKER_API_SECRET` 等敏感配置项。
- [x] **[WebUI]** 增强 WebUI，以展示持仓、订单和**回测报告**。
- [x] **[文档]** 完整更新文档，说明如何配置和启用真实交易模式，并附上**非常醒目的风险提示和免责声明**。

## Phase 3: 扩展功能 (Future Enhancements)

-   **依赖关系**: 在核心功能稳定运行后。

- [x] **[做空支持]** 扩展 `AbstractBroker` 接口以支持融券操作。
- [x] **[多策略支持]** 允许用户在多种预设的交易策略之间进行选择。
- [x] **[更丰富的分析指标]** 将更多技术指标集成到 `DecisionAgent` 和 `TradingStrategy` 的决策过程中。

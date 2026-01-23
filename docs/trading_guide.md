# 📖 自动交易与回测功能操作手册

本文档是 A股智能分析系统新增的 **自动交易** 与 **历史回测** 功能的详细操作指南。

> ⚠️ **重要提示**: 自动交易涉及真实的资金风险。在启用实盘交易前，请务必充分理解本手册内容，并在**模拟盘**和**历史回测**中对您的策略进行完整测试。

## 目录
- [功能概述](#功能概述)
- [新增配置详解](#新增配置详解)
  - [交易与回测配置](#交易与回测配置)
  - [LLM Agent 配置](#llm-agent-配置-双层模型架构)
- [如何运行模拟交易](#如何运行模拟交易-paper-trading)
- [如何运行历史回测](#如何运行历史回测-backtesting)
- [如何解读回测报告](#如何解读回测报告)
- [风险提示与免责声明](#风险提示与免责声明)

---

## 功能概述

新版系统在原有分析推送的基础上，增加了三大核心功能，形成了一个完整的“**分析 -> 验证 -> 交易**”闭环：

1.  **双层 LLM 架构 (Two-Tier LLM Architecture)**
    -   **摘要 Agent (Summarizer Agent)**: 使用一个轻量级、低成本的小模型（如 `gemini-3-flash-preview` 或本地 `Ollama` 模型），对海量新闻进行预处理和摘要，大幅降低 Token 消耗。
    -   **决策 Agent (Decision Agent)**: 使用能力更强的大模型（如 `gemini-1.5-pro`），在接收“技术面数据”和“新闻摘要”后，专注于做出高质量的买卖决策。

2.  **模拟交易 (Paper Trading)**
    -   系统会根据分析结果，在一个**完全虚拟的账户**中模拟真实的买卖操作。
    -   所有交易记录、持仓和资金变动都保存在本地数据库中，**不涉及任何真实资金**。
    -   这是验证策略有效性、观察策略在真实市场环境下表现的最佳方式。

3.  **历史回测 (Backtesting)**
    -   允许您在过去的一段时间（如去年一整年）的历史数据上，快速验证一个交易策略的表现。
    -   引擎会严格按照时间顺序“回放”历史，杜绝“未来函数”，科学地评估策略的**总回报率**、**最大回撤**和**夏普比率**等关键指标。

---

## 新增配置详解

所有新配置都在您的 `.env` 文件中设置。

### 交易与回测配置

这些配置项位于 `.env` 文件的 `[交易与回测配置]` 部分。

| 变量名 | 必填 | 说明 | 示例 |
|---|---|---|---|
| `TRADING_MODE` | 否 | **交易模式**。可选值：<br>- `paper` (默认): 模拟盘模式。执行交易决策，但所有操作只在本地数据库模拟。<br>- `live`: 实盘模式。**（高风险！暂未实现）** | `paper` |
| `TRADING_BROKER` | 否 | **经纪商（券商）**。目前只支持 `paper`。未来可扩展为真实券商的适配器名称。 | `paper` |
| `TRADING_CAPITAL` | 否 | **初始资金**。在**首次**运行模拟盘或每次**新的回测**时，系统会创建的初始虚拟资金。 | `100000.0` |
| `TRADING_MAX_POSITION_PER_STOCK` | 否 | **单只股票最大持仓金额**。这是一个风控参数，限制系统在单只股票上投入过多资金。 | `20000.0` |

### LLM Agent 配置 (双层模型架构)

这些配置项位于 `.env` 文件的 `[LLM Agent 配置]` 部分，用于配置**摘要 Agent**。

| 变量名 | 必填 | 说明 | 示例 |
|---|---|---|---|
| `SUMMARIZER_MODEL_TYPE` | 否 | **摘要模型的类型**。可选值：<br>- `gemini` (默认): 使用 Google Gemini 系列模型。<br>- `openai`: 使用 OpenAI 兼容 API（如 DeepSeek）。<br>- `ollama`: 使用本地 Ollama 模型。 | `gemini` |
| `SUMMARIZER_MODEL_NAME` | 否 | **摘要模型的具体名称**。根据 `SUMMARIZER_MODEL_TYPE` 填写。<br>- `gemini`: `gemini-3-flash-preview`<br>- `openai`: `deepseek-chat`<br>- `ollama`: `qwen:7b` | `gemini-3-flash-preview` |
| `SUMMARIZER_API_KEY` | 可选 | **摘要模型的 API Key**。如果摘要模型与决策模型使用不同的 Key，在此处填写。如果留空，则默认使用主模型的 `GEMINI_API_KEY` 或 `OPENAI_API_KEY`。 | |
| `SUMMARIZER_BASE_URL` | 可选 | **摘要模型的 API 地址**。主要用于 `openai` 或 `ollama` 类型。<br>- `ollama` 示例: `http://localhost:11434/v1` | `http://localhost:11434/v1` |

---

## 如何运行模拟交易 (Paper Trading)

模拟交易是默认开启的，它会在您正常运行每日分析时自动执行。

**步骤:**

1.  **检查配置**: 确保您的 `.env` 文件中 `TRADING_MODE` 设置为 `paper`（或直接注释掉该行，系统会默认使用 `paper`）。
2.  **正常运行分析**:
    ```bash
    # 运行一次完整的分析和模拟交易
    python main.py
    
    # 或者，如果您使用定时任务，它也会在每次定时任务中自动执行模拟交易
    python main.py --schedule
    ```
3.  **查看结果**:
    -   **日志**: 在程序运行的日志中，您会看到类似 `[交易引擎]` 开头的日志，记录了每一笔模拟交易的决策和执行情况。
    -   **数据库**: （进阶）您可以使用 `python test_env.py --db` 命令或任何 SQLite 客户端打开 `data/stock_analysis.db` 文件，查看 `trading_orders`、`trading_positions` 和 `trading_trades` 表来获取详细的交易数据。

---

## 如何运行历史回测 (Backtesting)

您需要创建一个单独的 Python 脚本来调用回测引擎。

**步骤:**

1.  **创建回测脚本**: 在项目根目录下创建一个新文件，例如 `run_backtest.py`。
2.  **编写脚本内容**:

    ```python
    # run_backtest.py
    import logging
    from datetime import date
    
    from trading.backtester import Backtester
    from main import setup_logging

    # 1. 初始化日志
    setup_logging(debug=True)
    
    # 2. 定义回测参数
    stock_codes_to_test = ["600519", "300750"]  # 您想回测的股票列表
    start_date = date(2023, 1, 1)              # 回测开始日期
    end_date = date(2023, 12, 31)             # 回测结束日期

    # 3. 初始化并运行回测引擎
    backtester = Backtester()
    report = backtester.run(
        stock_codes=stock_codes_to_test,
        start_date=start_date,
        end_date=end_date
    )

    # 4. 打印报告
    logging.info("回测完成！")
    logging.info("="*30 + " 回测绩效报告 " + "="*30)
    for key, value in report.items():
        logging.info(f"{key:<20}: {value}")
    logging.info("="*75)
    ```

3.  **运行回测**:
    ```bash
    python run_backtest.py
    ```
    回测过程会比较长，因为它需要按天模拟每一天的分析和交易。请耐心等待。

---

## 如何解读回测报告

回测结束后，您会看到一份类似下面这样的绩效报告：

```
session_id          : backtest_xxxxxxxx
start_date          : 2023-01-01
end_date            : 2023-12-31
initial_capital     : 100,000.00
final_assets        : 115,234.50
total_return_rate   : 15.23%
annualized_return   : 15.23%
max_drawdown        : -8.75%
sharpe_ratio        : 1.25
```

-   **Total Return Rate (总回报率)**: 整个回测期间的总收益率。
-   **Annualized Return (年化回报率)**: 将总回报率转换为年度标准，方便与其它投资产品比较。
-   **Max Drawdown (最大回撤)**: **（非常重要的风险指标）** 表示在整个回测期间，资产从最高点回落到最低点的最大幅度。这个值越小，说明策略的稳定性越好。`-8.75%` 意味着您的账户在最糟糕的情况下，从顶点亏损了 8.75%。
-   **Sharpe Ratio (夏普比率)**: **（非常重要的绩效指标）** 表示每承受一单位风险，可以获得多少超额回报。这个值越高，说明策略的“性价比”越高。通常大于 1 就算不错，大于 2 则相当优秀。

---

## 风险提示与免责声明

-   **历史不代表未来**: 回测表现好，不保证未来实盘也能盈利。市场风格会切换，策略可能会失效。
-   **滑点和交易成本**: 本系统的回测和模拟盘**没有考虑**交易成本（手续费、印花税）和滑点（下单价与实际成交价的差异）。这会导致回测结果比实际情况更乐观。
-   **永远从模拟盘开始**: 在您对一个策略非常有信心之前，请至少让它在模拟盘运行数周或数月。
-   **本项目不构成任何投资建议**。所有基于本系统产生的交易决策，无论是模拟还是实盘，其一切后果均由您本人承担。股市有风险，投资需谨慎。

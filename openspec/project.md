# Project Context

## Purpose
本项目的目标是打造一个基于 AI 大模型的 A/H 股自选股智能分析系统。它能够每日自动从多个数据源（如 AkShare, Efinance）获取股票行情和新闻数据，进行技术面、筹码分布和舆情分析，并最终生成一个包含核心结论、买卖点位和检查清单的“决策仪表盘”。**新版本增加了实盘交易能力，支持通过量化接口或模拟人工操作进行真实交易。**

该系统被设计为可通过 GitHub Actions 实现零成本、自动化部署和每日定时运行，并将分析结果推送到企业微信、飞书、Telegram、邮件等多个渠道。

## Tech Stack
- **语言**: Python 3.10+
- **核心框架**:
  - **Web 服务**: `FastAPI` + `Uvicorn` 提供高性能异步 Web API，前端使用 `Vue.js`。
  - **调度**: `schedule` 用于基本的定时任务。
  - **数据库**: `SQLAlchemy` ORM (2.0+)，默认使用 `SQLite` 进行数据持久化。
  - **交易接口**: `TigerOpen SDK` 用于老虎证券 API 对接。
  - **UI 自动化**: `Playwright` 用于模拟人工操作（可选，高风险）。
- **数据处理与分析**:
  - `pandas` (2.0+) 和 `numpy` (1.24+) 用于数据处理和数值计算。
- **AI 与大模型**:
  - `google-generativeai` (Google Gemini) 作为主要的 AI 分析引擎，默认模型 `gemini-3-flash-preview`。
  - `openai` (1.0+) 库以支持 OpenAI 兼容的 API (如 DeepSeek, 通义千问, Moonshot 等) 作为备选。
  - `langgraph` (0.2+) 用于 LLM Agent 工作流编排，实现多 Agent 协作分析。
  - `langchain-core` (0.2+) 提供 Agent 基础能力。
- **数据源**:
  - **行情数据**: `efinance` (优先级0), `akshare` (优先级1), `tushare` (优先级2), `baostock` (优先级3), `yfinance` (优先级4，备用)。
  - **新闻舆情**: `tavily-python`, `google-search-results` (SerpAPI), `bocha` (博查搜索，中文优化)。
- **消息通知**:
  - `lark-oapi` 用于飞书通知和云文档生成。
  - `requests` 用于调用企业微信、Telegram、自定义 Webhook 等。
  - Python 标准库 `smtplib` 用于邮件通知。
  - 支持 Pushover 手机推送。
- **交易与回测**:
  - 内置交易引擎 (`trading/engine.py`)，支持模拟交易 (`paper`) 和实盘交易 (`live`)。
  - 策略系统 (`trading/strategy.py`)，支持策略注册和切换。
  - 回测引擎 (`trading/backtester.py`)，支持历史数据回测。
- **部署与 CI/CD**:
  - **自动化**: GitHub Actions 用于 CI 和每日定时分析任务。
  - **容器化**: Docker (`Dockerfile`, `docker-compose.yml`)。
  - **测试**: `pytest`, `httpx` (用于 FastAPI 测试), `playwright` (E2E 测试)。

## Project Conventions

### Code Style
- **代码规范**: 严格遵循 **PEP 8** 指南。
- **格式化**: 使用 `black` 进行代码格式化，`isort` 进行 import 排序。
- **静态检查**: 使用 `flake8` 进行代码风格和逻辑错误检查。
- **文档字符串**: 所有公共模块、类和函数都必须包含符合标准的 Docstring。
- **类型提示**: 代码库广泛使用 Python 的类型提示以增强可读性和健壮性。

### Architecture Patterns
- **模块化设计**: 项目采用清晰的模块化结构，将不同职责分离到独立的包或模块中：
  - `data_provider/`: 封装了所有外部数据源的获取逻辑，提供统一的数据获取接口 (`DataFetcherManager`)，支持多数据源优先级和自动降级。
  - `web/`: FastAPI 应用，提供 RESTful API 和 WebSocket 支持，前端使用 Vue.js 构建。
    - `web/api/`: API 路由模块（config, news, analysis, trading）。
    - `web/frontend/`: Vue.js 前端应用。
  - `analysis/`: LLM Agent 分析模块。
    - `analysis/orchestrator.py`: LangGraph 工作流协调器 (`LLMOrchestrator`)，协调多个 Agent。
    - `analysis/agents/`: Agent 实现（`SummarizerAgent`, `DecisionAgent`）。
  - `trading/`: 交易引擎模块。
    - `trading/engine.py`: 交易引擎 (`TradingEngine`)，整合策略和经纪商。
    - `trading/strategy.py`: 策略系统，支持策略注册和切换。
    - `trading/backtester.py`: 回测引擎。
    - `trading/brokers/`: 经纪商适配器（`PaperBroker` 等）。
  - `stock_analyzer.py`: 趋势分析器，基于技术指标（MA、乖离率等）进行趋势判断。
  - `market_analyzer.py`: 大盘复盘分析器。
  - `notification.py`: 统一管理所有消息推送渠道 (`NotificationService`)。
  - `storage.py`: 数据库管理 (`DatabaseManager`)，负责数据的存储和读取，支持断点续传。
  - `scheduler.py`: 负责编排和调度整个每日分析流程。
  - `search_service.py`: 新闻搜索服务 (`SearchService`)，支持多搜索引擎负载均衡。
- **LLM Agent 架构**: 采用 LangGraph 实现多 Agent 协作工作流：
  - **工作流**: `search` → `summarize` → `decision`
  - **SummarizerAgent**: 负责对原始新闻进行摘要，降低 token 消耗。
  - **DecisionAgent**: 负责综合分析技术面、新闻摘要等，生成最终决策建议。
- **服务层抽象**: 在 Web 模块和核心逻辑中，通过服务层来解耦业务逻辑和底层实现。
- **策略模式**: 交易策略采用策略注册表模式 (`strategy_registry`)，支持动态切换策略。
- **适配器模式**: 数据源和经纪商采用适配器模式，便于扩展新的数据源或交易接口。

### Testing Strategy
- **静态检查优先**: CI 流程的核心是静态检查，确保代码质量和基础的正确性。
  - **语法检查**: 使用 `python -m py_compile` 保证所有 Python 文件语法无误。
  - **代码格式化**: `black` (行长度120) 和 `isort` 确保代码风格一致。
  - **严重错误检查**: `flake8` 用于捕获未定义变量、语法错误等严重问题。
  - **模块导入测试**: 简单的导入测试确保各核心模块可以被正常加载。
- **单元测试**: 使用 `pytest` (8.2+) 进行单元测试，`httpx` 用于 FastAPI API 测试。
- **E2E 测试**: 使用 `playwright` (1.44+) 进行端到端测试。
- **安全扫描**: 使用 `bandit` 进行代码安全漏洞扫描（跳过测试目录和 assert 语句）。
- **构建验证**: CI 流程包含一个 Docker 构建步骤，以验证 `Dockerfile` 的正确性和应用的容器化能力。

### Git Workflow
- **分支模型**: 功能开发在 `feature/` 分支上进行，Bug 修复在 `fix/` 分支上。所有开发完成后，向 `main` 分支发起 Pull Request。
- **Commit 规范**: 严格遵循 **Conventional Commits** 规范。Commit 消息必须包含类型前缀，如 `feat:`, `fix:`, `docs:`, `refactor:` 等。
- **Pull Request**: PR 是代码合入的唯一途径。PR 需要通过 CI 中的所有自动化检查。

## Domain Context
- **A/H 股**: 项目主要关注中国 A 股和香港 H 股市场。股票代码需要符合相应市场的格式（A股：6位数字，H股：5位数字）。
- **决策仪表盘**: 这是项目的核心产出，是一个结构化的分析摘要，包含明确的“买入/观望/卖出”建议、关键价位（买入价、止损价、目标价）以及一个基于预设交易理念的检查清单。
- **实盘交易**: 系统支持与真实券商进行交易，包括通过官方API和模拟人工操作两种方式。此功能涉及真实资金风险和法律合规性。
- **交易理念**: 内置了一套基础的交易原则，例如“严禁追高”（通过乖离率判断）、“趋势交易”（通过均线排列判断）等。AI 分析应遵循这些原则。

## Important Constraints
- **零成本运行**: 项目的一个核心设计约束是能够在 GitHub Actions 的免费额度内运行，避免用户产生服务器费用。这影响了技术选型和任务执行方式。
- **API 依赖**: 项目高度依赖外部 API，需要妥善处理：
  - **AI 模型 API**: Gemini (Google AI Studio 免费额度) 或 OpenAI 兼容 API (DeepSeek、通义千问等)。
  - **数据 API**: AkShare (免费)、Tushare Pro (需要 Token)、Baostock (免费)、YFinance (免费)。
  - **搜索 API**: Tavily (每月1000次免费)、SerpAPI (每月100次免费)、Bocha (需要 API Key)。
  - **配置方式**: API 密钥通过 GitHub Secrets 或 `.env` 文件配置。
  - **失败重试**: 使用 `tenacity` (8.2+) 实现指数退避重试机制。
- **并发控制**: 为避免触发反爬机制，默认并发数较低（`max_workers=3`），可通过配置调整。
- **消息长度限制**: 
  - 飞书：约 20KB（`feishu_max_bytes=20000`）。
  - 企业微信：4096 字节（`wechat_max_bytes=4000`）。
  - 超长消息自动分批发送。
- **数据库**: 使用 SQLite，支持断点续传（当日数据已存在则跳过获取）。

## External Dependencies
- **AI 模型服务**:
  - **Google AI Studio**: 用于获取免费的 Gemini API Key，是 AI 分析功能的核心。默认使用 `gemini-3-flash-preview` 模型。
  - **OpenAI 兼容 API**: 支持 DeepSeek、通义千问、Moonshot、Claude 等，作为 Gemini 的备选。
- **数据服务商**: 
  - **AkShare**: 免费，优先级最高，提供 A 股、H 股行情数据。
  - **Tushare Pro**: 需要 Token，提供专业级数据。
  - **Baostock**: 免费，证券宝数据源。
  - **YFinance**: 免费，Yahoo Finance，主要用于备用。
  - **Efinance**: 免费，东方财富数据源，优先级最高。
- **搜索服务**: 
  - **Tavily**: 每月 1000 次免费搜索，支持 AI 摘要。
  - **SerpAPI**: 每月 100 次免费搜索，Google 搜索结果。
  - **Bocha (博查搜索)**: 中文搜索优化，支持 AI 摘要，需要 API Key。
- **通知渠道**: 
  - **企业微信**: 通过 Webhook URL 推送。
  - **飞书**: 通过 Webhook URL 推送，支持云文档生成（需要 App ID/Secret）。
  - **Telegram**: 通过 Bot Token 和 Chat ID 推送。
  - **邮件**: 通过 SMTP 发送（支持 QQ、Gmail 等）。
  - **Pushover**: 手机/桌面推送通知。
  - **自定义 Webhook**: 支持钉钉、Discord、Slack、Bark 等任意支持 POST JSON 的 Webhook。
- **部署平台**:
  - **GitHub Actions**: 用于 CI/CD 和每日定时任务执行（免费额度）。
  - **Docker**: 支持容器化部署。
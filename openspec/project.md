# Project Context

## Purpose
本项目的目标是打造一个基于 AI 大模型的 A/H 股自选股智能分析系统。它能够每日自动从多个数据源（如 AkShare, Efinance）获取股票行情和新闻数据，进行技术面、筹码分布和舆情分析，并最终生成一个包含核心结论、买卖点位和检查清单的“决策仪表盘”。

该系统被设计为可通过 GitHub Actions 实现零成本、自动化部署和每日定时运行，并将分析结果推送到企业微信、飞书、Telegram、邮件等多个渠道。

## Tech Stack
- **语言**: Python 3.10+
- **核心框架**:
  - **Web 服务**: 基于 Python 标准库 `http.server` 的自定义轻量级服务器，用于提供本地 WebUI。
  - **调度**: `schedule` 用于基本的定时任务。
  - **数据库**: `SQLAlchemy` ORM，默认使用 `SQLite` 进行数据持久化。
- **数据处理与分析**:
  - `pandas` 和 `numpy` 用于数据处理和数值计算。
- **AI 与大模型**:
  - `google-generativeai` (Google Gemini) 作为主要的 AI 分析引擎。
  - `openai` 库以支持 OpenAI 兼容的 API (如 DeepSeek, 通义千问等) 作为备选。
- **数据源**:
  - **行情**: `efinance`, `akshare`, `tushare`, `baostock`, `yfinance`。
  - **新闻舆情**: `tavily-python`, `google-search-results` (SerpAPI)。
- **消息通知**:
  - `lark-oapi` 用于飞书通知。
  - `requests` 用于调用企业微信、Telegram等的 Webhook。
  - Python 标准库 `smtplib` 用于邮件通知。
- **部署与 CI/CD**:
  - **自动化**: GitHub Actions 用于 CI 和每日定时分析任务。
  - **容器化**: Docker (`Dockerfile`, `docker-compose.yml`)。

## Project Conventions

### Code Style
- **代码规范**: 严格遵循 **PEP 8** 指南。
- **格式化**: 使用 `black` 进行代码格式化，`isort` 进行 import 排序。
- **静态检查**: 使用 `flake8` 进行代码风格和逻辑错误检查。
- **文档字符串**: 所有公共模块、类和函数都必须包含符合标准的 Docstring。
- **类型提示**: 代码库广泛使用 Python 的类型提示以增强可读性和健壮性。

### Architecture Patterns
- **模块化设计**: 项目采用清晰的模块化结构，将不同职责分离到独立的包或模块中：
  - `data_provider/`: 封装了所有外部数据源的获取逻辑，提供统一的数据获取接口。
  - `web/`: 包含自研的轻量级 Web 服务器，负责路由、请求处理和 HTML 模板渲染，为用户提供本地配置界面。
  - `analyzer.py`, `stock_analyzer.py`: 核心分析器，负责调用 AI 模型并整合数据生成分析报告。
  - `notification.py`: 统一管理所有消息推送渠道。
  - `storage.py`: 数据库管理，负责数据的存储和读取。
  - `scheduler.py`: 负责编排和调度整个每日分析流程。
- **服务层抽象**: 在 Web 模块和核心逻辑中，通过服务层（如 `ConfigService`, `AnalysisService`）来解耦业务逻辑和底层实现。

### Testing Strategy
- **静态检查优先**: CI 流程的核心是静态检查，确保代码质量和基础的正确性。
  - **语法检查**: 使用 `python -m py_compile` 保证所有 Python 文件语法无误。
  - **严重错误检查**: `flake8` 用于捕获未定义变量、语法错误等严重问题。
  - **模块导入测试**: 简单的导入测试确保各核心模块可以被正常加载。
- **单元测试**: 约定使用 `pytest` 进行单元测试（尽管目前 CI 中未强制执行）。
- **安全扫描**: 约定使用 `bandit` 进行代码安全漏洞扫描。
- **构建验证**: CI 流程包含一个 Docker 构建步骤，以验证 `Dockerfile` 的正确性和应用的容器化能力。

### Git Workflow
- **分支模型**: 功能开发在 `feature/` 分支上进行，Bug 修复在 `fix/` 分支上。所有开发完成后，向 `main` 分支发起 Pull Request。
- **Commit 规范**: 严格遵循 **Conventional Commits** 规范。Commit 消息必须包含类型前缀，如 `feat:`, `fix:`, `docs:`, `refactor:` 等。
- **Pull Request**: PR 是代码合入的唯一途径。PR 需要通过 CI 中的所有自动化检查。

## Domain Context
- **A/H 股**: 项目主要关注中国 A 股和香港 H 股市场。股票代码需要符合相应市场的格式。
- **决策仪表盘**: 这是项目的核心产出，是一个结构化的分析摘要，包含明确的“买入/观望/卖出”建议、关键价位（买入价、止损价、目标价）以及一个基于预设交易理念的检查清单。
- **交易理念**: 内置了一套基础的交易原则，例如“严禁追高”（通过乖离率判断）、“趋势交易”（通过均线排列判断）等。AI 分析应遵循这些原则。

## Important Constraints
- **零成本运行**: 项目的一个核心设计约束是能够在 GitHub Actions 的免费额度内运行，避免用户产生服务器费用。这影响了技术选型和任务执行方式。
- **API 依赖**: 项目高度依赖外部 API，包括 AI 模型 API (Gemini/OpenAI) 和数据 API (AkShare 等)。需要妥善处理 API 密钥的配置（通过 GitHub Secrets）和网络请求的失败重试（使用 `tenacity`）。

## External Dependencies
- **Google AI Studio**: 用于获取免费的 Gemini API Key，是 AI 分析功能的核心。
- **数据服务商**: AkShare, Tushare, Baostock, YFinance 等是行情数据的来源。
- **搜索服务**: Tavily, SerpAPI 等用于获取最新的新闻和舆情信息。
- **通知渠道**: 企业微信、飞书、Telegram 等，需要用户配置各自的 Webhook URL 或 Bot Token。
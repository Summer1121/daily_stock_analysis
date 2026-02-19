# 任务清单：控制台

这是一个将大型任务分解为小块、可管理的步骤的清单。

- [x] **1. 环境搭建**
    - [x] 1.1. 在 `requirements.txt` 中增加 `fastapi`, `uvicorn`, `websockets` 等后端依赖。
    - [x] 1.2. 创建 `web/` 目录用于存放所有 Web 相关的前端代码。
    - [x] 1.3. 在 `web/` 目录下初始化一个 Vue.js 项目。
    - [x] 1.4. 配置 Vue.js 项目，使其能够与 FastAPI 后端协同工作（例如，配置代理以避免 CORS 问题）。

- [x] **2. 后端 API 开发 (FastAPI)**
    - [x] 2.1. 创建一个基础的 FastAPI 应用实例。
    - [x] 2.2. 实现 `/api/config` 端点，用于读取和更新系统配置。
    - [x] 2.3. 实现 `/api/news` 端点，提供实时新闻数据（可通过 WebSocket 推送）。
    - [x] 2.4. 实现 `/api/analysis` 端点，用于获取历史分析记录。
    - [x] 2.5. 实现 `/api/trading/dashboard` 端点，提供交易看板数据。
    - [x] 2.6. 实现 `/api/strategies` 端点族，用于管理策略。
    - [x] 2.7. 实现 `/api/trading/order` 端点，用于手动下单。
    - [x] 2.8. 编写后端的单元测试以确保 API 的正确性。
    - [x] 2.9. 实现 `/api/trading/backtest` 端点，用于执行策略回测。

- [x] **3. 前端界面开发 (Vue.js)**
    - [x] 3.1. 设计并实现控制台的整体布局（导航栏、侧边栏、主内容区）。
    - [x] 3.2. 开发“配置管理”页面，并与 `/api/config` 对接。
    - [x] 3.3. 开发“实时新闻”模块，并与 `/api/news` 对接（使用 WebSocket）。
    - [x] 3.4. 开发“走势分析记录”页面，并与 `/api/analysis` 对接。
    - [x] 3.5. 开发“交易看板”页面，并与 `/api/trading/dashboard` 对接。
    - [x] 3.6. 开发“策略管理”页面，并与 `/api/strategies` 对接。
    - [x] 3.7. 开发“手动交易”模块，并与 `/api/trading/order` 对接。
    - [x] 3.8. 开发“策略回测”页面，并与 `/api/trading/backtest` 对接。

- [x] **4. 集成与替换**
    - [x] 4.1. 调整 `main.py` 或创建一个新的启动脚本，使用 `uvicorn` 来运行 FastAPI 应用，并让 FastAPI 托管 Vue.js 的静态文件。
    - [x] 4.2. 确保在 Docker 环境中也能正确构建和运行新的前后端应用。
    - [x] 4.3. 编写端到端 (E2E) 测试，模拟用户在浏览器中的操作，验证整个流程。

- [x] **5. 文档**
    - [x] 5.1. 更新 `README.md`，说明如何启动和使用新的控制台。
    - [x] 5.2. 为新的 API 编写文档（FastAPI 的自动文档可以作为基础）。

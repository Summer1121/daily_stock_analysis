# 设计文档：控制台

## 1. 架构概述

为了实现功能丰富、交互流畅的控制台，我们建议采用前后端分离的现代 Web 架构。

- **前端**: 使用 **Vue.js** 框架构建一个单页面应用 (SPA)。Vue.js 以其易用性、灵活性和丰富的生态系统而闻名，非常适合快速开发高质量的用户界面。我们将使用现有的 `webui.py` 作为基础，并将其扩展为一个功能齐全的 Web 服务器。
- **后端**: 放弃当前简陋的 `http.server`，引入 **FastAPI** 框架来构建强大的 RESTful API。FastAPI 性能卓越，原生支持异步，并能自动生成交互式 API 文档 (Swagger UI)，这将极大地方便前端开发和后续的 API 维护。
- **通信**: 前后端之间通过标准的 JSON 格式进行数据交换。

## 2. 技术选型与理由

| 模块 | 技术选型 | 理由 |
| --- | --- | --- |
| 后端 API 框架 | FastAPI | 性能高，支持异步，自动生成 API 文档，拥有强大的依赖注入系统，非常适合构建现代 Web 服务。相比 Flask 或 Django，它更轻量、更现代。 |
| 前端框架 | Vue.js | 学习曲线平缓，组件化开发模式清晰，生态系统成熟（Vue Router, Pinia），能够满足复杂界面的需求。 |
| UI 组件库 | Element Plus / Ant Design Vue | 提供一套高质量、开箱即用的 UI 组件，可以显著加快开发速度，并保证界面风格的统一和美观。 |
| 实时通信 | WebSocket | 用于实现实时新闻推送、交易看板的实时更新等功能。FastAPI 对 WebSocket 有着良好的原生支持。 |

## 3. 后端 API 设计

新的 FastAPI 应用将挂载在 `/api` 路径下，以避免与前端静态文件路由冲突。以下是初步的 API 端点设计：

- `GET /api/news`: 获取实时新闻流。
- `GET /api/analysis`: 获取历史分析记录。
- `GET /api/config`: 获取当前系统配置（信息渠道、推送、策略等）。
- `POST /api/config`: 更新系统配置。
- `GET /api/trading/dashboard`: 获取交易看板数据（持仓、盈利等）。
- `POST /api/trading/order`: 执行手动交易下单。
- `GET /api/strategies`: 获取所有可用策略及其状态。
- `POST /api/strategies/{strategy_name}/toggle`: 启用/禁用特定策略。
- `POST /api/trading/backtest`: 启动策略回测，接受策略名称、时间区间等参数。

## 4. 前端架构

前端将遵循标准的 Vue.js 项目结构：

- **`main.js`**: 应用入口，初始化 Vue 实例和插件。
- **`router/index.js`**: 使用 `vue-router` 定义前端路由，每个主要功能模块（如新闻、交易、配置）对应一个路由。
- **`store/index.js`**: 使用 `pinia` 作为状态管理库，管理应用的全局状态（如用户信息、系统配置等）。
- **`views/`**: 存放页面级别的组件。
- **`components/`**: 存放可复用的基础组件。
- **`api/`**: 封装所有对后端 API 的请求。

## 5. 集成计划

我们将分阶段进行集成：

1. **搭建基础环境**: 首先搭建 FastAPI 和 Vue.js 的开发环境，并完成基本的项目结构创建。
2. **迁移现有功能**: 将 `webui.py` 中现有的配置功能迁移到新的控制台界面中。
3. **开发新功能**: 逐一实现提案中要求的新功能模块（新闻、交易看板等）。
4. **替换 Web 服务器**: 当新控制台功能完备后，在 `main.py` 中用 FastAPI 服务器 (`uvicorn`) 替换掉现有的 `http.server`。

## 6. 风险与考量

- **依赖增加**: 引入 FastAPI 和 Vue.js 会增加项目的依赖。我们需要更新 `requirements.txt` 和 `package.json`（如果使用 npm/yarn 管理前端依赖）。
- **开发复杂性**: 相比于简单的 `http.server`，前后端分离的架构对开发和部署的要求更高。
- **学习成本**: 团队成员可能需要时间熟悉 FastAPI 和 Vue.js。

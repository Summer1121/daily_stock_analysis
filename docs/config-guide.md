# ⚙️ 配置指南（环境变量与功能）

**快速查阅**：需要准备哪些配置、每项做什么用，请先看 **[配置准备清单](配置准备清单.md)**。本文档是环境变量的完整列表与说明，便于按需查阅和进阶配置。

---

## 环境变量完整列表

### AI 模型配置

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|:----:|
| `GEMINI_API_KEY` | Google Gemini API Key（[Google AI Studio](https://aistudio.google.com/) 获取） | - | ✅* |
| `GEMINI_MODEL` | Gemini 主模型名称 | `gemini-3-flash-preview` | 可选 |
| `GEMINI_MODEL_FALLBACK` | Gemini 限流/失败时备选模型 | `gemini-2.5-flash` | 可选 |
| `GEMINI_REQUEST_DELAY` | 请求间隔（秒），用于降低限流概率 | `2.0` | 可选 |
| `GEMINI_MAX_RETRIES` | 最大重试次数 | `5` | 可选 |
| `GEMINI_RETRY_DELAY` | 重试基础延时（秒） | `5.0` | 可选 |
| `OPENAI_API_KEY` | OpenAI 兼容 API Key（DeepSeek、通义千问、Moonshot 等） | - | 可选 |
| `OPENAI_BASE_URL` | OpenAI 兼容 API 的 base URL（如 `https://api.deepseek.com/v1`） | - | 可选 |
| `OPENAI_MODEL` | OpenAI 兼容模型名称 | `gpt-4o-mini` | 可选 |

\* `GEMINI_API_KEY` 与 `OPENAI_API_KEY` 至少配置一个，AI 分析功能才可用。

### 通知渠道配置

| 变量名 | 说明 | 必填 |
|--------|------|:----:|
| `WECHAT_WEBHOOK_URL` | 企业微信机器人 Webhook URL | 可选 |
| `FEISHU_WEBHOOK_URL` | 飞书机器人 Webhook URL | 可选 |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token（@BotFather 获取） | 可选 |
| `TELEGRAM_CHAT_ID` | Telegram 接收会话的 Chat ID | 可选 |
| `EMAIL_SENDER` | 发件人邮箱 | 可选 |
| `EMAIL_PASSWORD` | 邮箱 SMTP 授权码（非登录密码） | 可选 |
| `EMAIL_RECEIVERS` | 收件人邮箱，多个用逗号分隔；留空则发给自己 | 可选 |
| `PUSHOVER_USER_KEY` | Pushover 用户 Key | 可选 |
| `PUSHOVER_API_TOKEN` | Pushover 应用 API Token | 可选 |
| `CUSTOM_WEBHOOK_URLS` | 自定义 Webhook 地址（钉钉、Discord、Slack 等），多个用逗号分隔 | 可选 |
| `CUSTOM_WEBHOOK_BEARER_TOKEN` | 自定义 Webhook 的 Bearer 鉴权 Token | 可选 |
| `SINGLE_STOCK_NOTIFY` | 设为 `true` 则每分析完一只股票立即推送，否则汇总后推送 | 可选 |
| `FEISHU_MAX_BYTES` | 飞书单条消息最大字节数（超长自动分批） | `20000` |
| `WECHAT_MAX_BYTES` | 企业微信单条消息最大字节数 | `4000` |

### 搜索服务配置（新闻/舆情）

| 变量名 | 说明 | 必填 |
|--------|------|:----:|
| `TAVILY_API_KEYS` | Tavily 搜索 API Key，多个用逗号分隔 | 推荐 |
| `BOCHA_API_KEYS` | 博查搜索 API Key（中文优化），多个用逗号分隔 | 可选 |
| `SERPAPI_API_KEYS` | SerpAPI Key，多个用逗号分隔 | 可选 |

### 数据源配置

| 变量名 | 说明 | 必填 |
|--------|------|:----:|
| `TUSHARE_TOKEN` | Tushare Pro Token；不配则使用 AkShare 等免费源 | 可选 |

### 飞书云文档

| 变量名 | 说明 | 必填 |
|--------|------|:----:|
| `FEISHU_APP_ID` | 飞书开放平台应用 App ID | 可选 |
| `FEISHU_APP_SECRET` | 飞书开放平台应用 App Secret | 可选 |
| `FEISHU_FOLDER_TOKEN` | 存放日报的云文档文件夹 Token | 可选 |

### 系统与运行

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `STOCK_LIST` | 自选股代码，逗号分隔（如 `600519,300750`）；港股加 `hk` 前缀 | 必填 |
| `DATABASE_PATH` | SQLite 数据库文件路径 | `./data/stock_analysis.db` |
| `LOG_DIR` | 日志目录 | `./logs` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `MAX_WORKERS` | 分析并发线程数 | `3` |
| `DEBUG` | 设为 `true` 开启调试 | `false` |
| `SCHEDULE_ENABLED` | 是否启用定时任务 | `false` |
| `SCHEDULE_TIME` | 每日执行时间（HH:MM） | `18:00` |
| `MARKET_REVIEW_ENABLED` | 是否执行大盘复盘 | `true` |
| `WEBUI_ENABLED` | 是否启动 Web 控制台 | `false` |
| `WEBUI_HOST` | WebUI 监听地址 | `127.0.0.1` |
| `WEBUI_PORT` | WebUI 端口 | `8000` |

### 交易与回测

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `TRADING_MODE` | `paper` 模拟盘，`live` 实盘 | `paper` |
| `TRADING_BROKER` | 实盘时：`real_api` 或 `real_ui_automation` | `paper` |
| `TRADING_CAPITAL` | 初始资金（元） | `100000.0` |
| `TRADING_MAX_POSITION_PER_STOCK` | 单股最大持仓金额（元） | `20000.0` |
| `REAL_BROKER_TYPE` | 实盘券商标识（如 `tiger`、`ths_web`） | - |
| `REAL_BROKER_API_KEY` | 实盘 API Key（量化接口） | - |
| `REAL_BROKER_API_SECRET` | 实盘 API Secret 或 RSA 私钥 | - |
| `REAL_BROKER_ACCOUNT` | 实盘交易账号（UI 自动化） | - |
| `REAL_BROKER_PASSWORD` | 实盘交易密码（UI 自动化，敏感） | - |
| `UI_AUTOMATION_BROWSER` | 浏览器类型：`chrome` / `firefox` / `edge` | `chrome` |
| `UI_AUTOMATION_HEADLESS` | 是否无头模式 | `true` |

---

## 通知渠道配置说明

### 企业微信 / 飞书

在群聊设置中添加「机器人」，获取 Webhook URL，填入对应环境变量即可。

### 邮件推送

需在邮箱中开启 SMTP 服务并获取「授权码」（不是登录密码），将发件人、授权码填入 `EMAIL_SENDER`、`EMAIL_PASSWORD`。

### 港股与高级功能

- **港股**：股票代码加 `hk` 前缀，如 `hk00700`。
- **双层模型**：可配置摘要用轻量模型、决策用强力模型以节省 Token，详见代码与 OpenSpec。

---

更多「需要准备哪些配置、每项作用」的总结见 **[配置准备清单](配置准备清单.md)**。

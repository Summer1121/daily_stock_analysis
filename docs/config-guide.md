# ⚙️ 配置指南 (环境变量与功能)

本文档包含系统所有环境变量的详细列表及其功能说明。

## 环境变量完整列表

### AI 模型配置

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|:----:|
| `GEMINI_API_KEY` | Google Gemini API Key | - | ✅* |
| `OPENAI_API_KEY` | OpenAI 兼容 API Key | - | 可选 |
| `OPENAI_BASE_URL` | API 代理地址 | - | 可选 |
| `OPENAI_MODEL` | 模型名称 | `gpt-4o` | 可选 |

### 通知渠道配置

| 变量名 | 说明 | 必填 |
|--------|------|:----:|
| `WECHAT_WEBHOOK_URL` | 企业微信机器人 | 可选 |
| `FEISHU_WEBHOOK_URL` | 飞书机器人 | 可选 |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | 可选 |
| `EMAIL_SENDER` | 发件人邮箱 | 可选 |

### 搜索服务配置

| 变量名 | 说明 | 必填 |
|--------|------|:----:|
| `TAVILY_API_KEYS` | Tavily 搜索 API | 推荐 |
| `BOCHA_API_KEYS` | 博查搜索（中文优化） | 可选 |

### 交易与回测配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `TRADING_MODE` | **交易模式**。可选值：`paper` (模拟盘), `live` (实盘)。实盘模式下需配置下方 `REAL_` 开头的变量。 | `paper` |
| `TRADING_BROKER` | **经纪商概念类型**。当 `TRADING_MODE` 为 `live` 时有效。可选值：`real_api` (量化接口), `real_ui_automation` (UI自动化)。 | `paper` |
| `TRADING_CAPITAL` | 初始资金。在**首次**运行模拟盘或每次**新的回测**时，系统会创建的初始虚拟资金。 | `100000.0` |
| `TRADING_MAX_POSITION_PER_STOCK` | 单只股票最大持仓金额。风控参数，限制系统在单只股票上投入过多资金。 | `20000.0` |
| `REAL_BROKER_TYPE` | **具体券商类型**。当 `TRADING_MODE` 为 `live` 时有效。例如：`tiger` (老虎证券), `ths_web` (同花顺网页版)。 | - |
| `REAL_BROKER_API_KEY` | **实盘 API Key**。当 `TRADING_BROKER` 为 `real_api` 时需要。例如：老虎证券的 `Tiger ID`。 | - |
| `REAL_BROKER_API_SECRET` | **实盘 API Secret**。当 `TRADING_BROKER` 为 `real_api` 时需要。例如：老虎证券的 RSA 私钥文件路径或私钥内容。 | - |
| `REAL_BROKER_ACCOUNT` | **实盘交易账号**。当 `TRADING_BROKER` 为 `real_ui_automation` 时需要。 | - |
| `REAL_BROKER_PASSWORD` | **实盘交易密码**。当 `TRADING_BROKER` 为 `real_ui_automation` 时需要。**敏感信息，建议加密存储或通过安全方式加载。** | - |
| `UI_AUTOMATION_BROWSER` | **UI自动化浏览器类型**。当 `TRADING_BROKER` 为 `real_ui_automation` 时有效。可选值：`chrome`, `firefox`, `edge`。 | `chrome` |
| `UI_AUTOMATION_HEADLESS` | **UI自动化无头模式**。当 `TRADING_BROKER` 为 `real_ui_automation` 时有效。可选值：`true` (无头模式), `false` (有头模式)。 | `true` |

## 通知渠道详细配置

### 1. 企业微信/飞书
在群聊设置中添加“机器人”，获取 Webhook URL 填入环境变量。

### 2. 邮件推送
需要开启邮箱的 SMTP 服务并获取“授权码”（非登录密码）。

---

## 数据源配置
系统默认使用 **AkShare** (免费)。如需更稳定的数据，可配置 `TUSHARE_TOKEN`。

---

## 高级功能
- **港股支持**: 股票代码加 `hk` 前缀，如 `hk00700`。
- **双层模型架构**: 使用轻量模型摘要，强力模型决策以节省 Token。

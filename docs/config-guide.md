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
| `TRADING_MODE` | 交易模式 (`paper`/`live`) | `paper` |
| `TRADING_CAPITAL` | 初始资金 | `100000.0` |

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

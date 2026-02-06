# 🌐 线上部署指南 (GitHub Actions)

本文档介绍如何在 GitHub Actions 上零成本部署和运行 A股智能分析系统。

## GitHub Actions 详细配置

### 1. Fork 本仓库

点击右上角 `Fork` 按钮。

### 2. 配置 Secrets

进入你 Fork 的仓库 → `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

#### AI 模型配置（二选一）

| Secret 名称 | 说明 | 必填 |
|------------|------|:----:|
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/) 获取免费 Key | ✅* |
| `OPENAI_API_KEY` | OpenAI 兼容 API Key | 可选 |
| `OPENAI_BASE_URL` | OpenAI 兼容 API 地址 | 可选 |
| `OPENAI_MODEL` | 模型名称 | 可选 |

#### 通知渠道配置

| Secret 名称 | 说明 | 必填 |
|------------|------|:----:|
| `WECHAT_WEBHOOK_URL` | 企业微信 Webhook URL | 可选 |
| `FEISHU_WEBHOOK_URL` | 飞书 Webhook URL | 可选 |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | 可选 |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID | 可选 |
| `EMAIL_SENDER` | 发件人邮箱 | 可选 |
| `EMAIL_PASSWORD` | 邮箱授权码 | 可选 |

#### 其他配置

| Secret 名称 | 说明 | 必填 |
|------------|------|:----:|
| `STOCK_LIST` | 自选股代码，如 `600519,300750` | ✅ |
| `TAVILY_API_KEYS` | Tavily 搜索 API（推荐） | 推荐 |

#### 实盘交易配置

| Secret 名称 | 说明 | 必填 |
|------------|------|:----:|
| `TRADING_MODE` | **交易模式** (`paper`/`live`) | 否 |
| `TRADING_BROKER` | **经纪商概念类型** (`real_api`/`real_ui_automation`) | 否 |
| `TRADING_CAPITAL` | 初始资金 | 否 |
| `TRADING_MAX_POSITION_PER_STOCK` | 单只股票最大持仓金额 | 否 |
| `REAL_BROKER_TYPE` | **具体券商类型** (如 `tiger`, `ths_web`) | 否 |
| `REAL_BROKER_API_KEY` | **实盘 API Key** (如老虎证券的 `Tiger ID`) | 否 |
| `REAL_BROKER_API_SECRET` | **实盘 API Secret** (如老虎证券的 RSA 私钥文件路径或内容) | 否 |
| `REAL_BROKER_ACCOUNT` | **实盘交易账号** (UI 自动化模式需要) | 否 |
| `REAL_BROKER_PASSWORD` | **实盘交易密码** (UI 自动化模式需要)。**警告: 敏感信息，不建议直接存放于 GitHub Secrets。** | 否 |
| `UI_AUTOMATION_BROWSER` | **UI自动化浏览器类型** (`chrome`, `firefox`, `edge`) | 否 |
| `UI_AUTOMATION_HEADLESS` | **UI自动化无头模式** (`true`/`false`) | 否 |

### 3. 启用 Actions

1. 点击顶部的 `Actions` 标签。
2. 点击 `I understand my workflows, go ahead and enable them`。

### 4. 手动测试

1. 选择 `每日股票分析` workflow。
2. 点击 `Run workflow` -> 选择模式 -> `Run workflow`。

### 5. 定时任务配置

编辑 `.github/workflows/daily_analysis.yml`:

```yaml
schedule:
  - cron: '0 10 * * 1-5'   # 周一到周五 18:00（北京时间）
```

| 北京时间 | UTC cron 表达式 |
|---------|----------------|
| 15:00 | `'0 7 * * 1-5'` |
| 18:00 | `'0 10 * * 1-5'` |

---

💡 **环境变量与高级配置**: 详细参数说明请参考 [配置指南](config-guide.md)。

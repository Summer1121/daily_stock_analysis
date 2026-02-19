# 🏠 本地部署指南 (Docker / Python)

本文档介绍如何在本地服务器、个人电脑或 Docker 容器中部署 A股智能分析系统。

## Docker 部署

### 快速启动

```bash
# 1. 克隆仓库
git clone https://github.com/ZhuLinsen/daily_stock_analysis.git
cd daily_stock_analysis

# 2. 配置环境变量
cp .env.example .env
vim .env  # 填入 API Key 和配置。**实盘交易需要额外配置，详见 [配置指南](config-guide.md)。**

# 3. 启动容器
docker-compose up -d webui      # WebUI 模式（推荐）
docker-compose up -d analyzer   # 定时任务模式
```

### 运行模式

| 命令 | 说明 | 端口 |
|------|------|------|
| `docker-compose up -d webui` | WebUI 模式，手动触发分析 | 8000 |
| `docker-compose up -d analyzer` | 定时任务模式，每日自动执行 | - |

---

## 本地运行 (Python)

### 安装依赖

```bash
pip install -r requirements.txt
# 如果使用 UI 自动化功能，需要安装 Playwright 浏览器驱动
# playwright install
```

### 命令行参数

```bash
python main.py                        # 完整分析
python main.py --webui-only           # 仅启动 WebUI
python main.py --stocks 600519,300750 # 指定股票
```

### 定时任务 (crontab)

```bash
# 启动定时模式
python main.py --schedule

# 或使用 crontab (周一到周五 18:00)
0 18 * * 1-5 cd /path/to/project && python main.py
```

---

## 本地 WebUI 管理界面

访问地址：`http://localhost:8000`

### 功能特性
- **配置管理**：实时修改自选股列表。
- **快速分析**：一键触发单只股票分析。
- **交易看板**：监控模拟盘盈亏。

---

💡 **环境变量与高级配置**: 详细参数说明请参考 [配置指南](config-guide.md)。

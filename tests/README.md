# E2E 测试

本目录包含系统端到端（E2E）测试，用于验证 WebUI 页面的可用性。

## 测试内容

### 页面可用性测试 (`test_pages.py`)

- **健康检查端点** (`/health`)
- **首页** (`/`)
- **静态资源**
- **API 端点** (`/analysis`, `/tasks`, `/task`)
- **错误处理** (404 页面)
- **性能测试** (响应时间、并发请求)

## 运行测试

### 前置条件

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 确保 playwright 浏览器已安装：

```bash
playwright install chromium
```

### 运行测试

#### 方式一：直接运行 pytest

```bash
# 运行所有测试
pytest tests/e2e/test_pages.py -v

# 运行特定测试
pytest tests/e2e/test_pages.py::TestPageAvailability::test_health_endpoint -v
```

#### 方式二：自动启动服务器

```bash
# pytest 会自动启动 Web 服务器（如果未运行）
pytest tests/e2e/ -v --tb=short
```

#### 方式三：手动启动服务器后运行

```bash
# 终端 1：启动 WebUI
python main.py --webui-only

# 终端 2：运行测试
pytest tests/e2e/ -v
```

## 测试配置

测试配置位于 `conftest.py` 中：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `BASE_URL` | `http://127.0.0.1:8000` | Web 服务器地址 |
| `SERVER_STARTUP_TIMEOUT` | 60秒 | 等待服务器启动的超时时间 |

可以通过环境变量覆盖：

```bash
TEST_BASE_URL=http://localhost:8000 pytest tests/e2e/ -v
```

## 测试报告

测试结束后，会生成 HTML 报告：

```bash
# 查看 HTML 报告
playwright show-report
```

## 持续集成

在 CI/CD 中运行测试：

```yaml
# .github/workflows/test.yml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium
      - name: Run E2E tests
        run: pytest tests/e2e/ -v
```

## 添加新测试

在 `test_pages.py` 中添加新的测试类或测试方法：

```python
class TestNewFeature:
    """新功能测试"""
    
    def test_new_endpoint(self, server_url: str):
        """测试新端点"""
        response = requests.get(f"{server_url}/new-endpoint")
        assert response.status_code == 200
```

## 故障排查

### 问题：服务器启动超时

- 检查端口 8000 是否被占用
- 手动启动服务器确认无错误

### 问题：测试失败

- 检查 `.env` 配置是否正确
- 查看日志输出

### 问题：import 错误

- 确保在项目根目录运行测试
- 检查 `PYTHONPATH` 是否包含项目根目录

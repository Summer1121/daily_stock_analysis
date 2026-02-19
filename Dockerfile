# ===================================
# A股自选股智能分析系统 - Docker 镜像
# ===================================

# --- Stage 1: Build Frontend ---
FROM node:18-slim as frontend-builder

WORKDIR /app/frontend

COPY web/frontend/package.json web/frontend/package-lock.json ./
RUN npm install

COPY web/frontend/ ./
RUN npm run build

# --- Stage 2: Final Image ---
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置时区为上海
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 复制应用代码
COPY . .

# 从前端构建阶段复制静态文件
COPY --from=frontend-builder /app/frontend/dist /app/web/frontend/dist

# 创建数据目录
RUN mkdir -p /app/data /app/logs /app/reports

# 设置环境变量默认值
ENV PYTHONUNBUFFERED=1
ENV LOG_DIR=/app/logs
ENV DATABASE_PATH=/app/data/stock_analysis.db
# WebUI应用
ENV WEBUI_HOST=0.0.0.0
ENV WEBUI_PORT=8000

# 暴露 WebUI 端口
EXPOSE 8000

# 数据卷（持久化数据）
VOLUME ["/app/data", "/app/logs", "/app/reports"]

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api || exit 1

# 默认命令
CMD ["uvicorn", "web.main:app", "--host", "0.0.0.0", "--port", "8000"]

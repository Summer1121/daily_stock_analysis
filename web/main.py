from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from web.api import config, news, analysis, trading

app = FastAPI(title="A股智能分析系统")

app.include_router(config.router, prefix="/api")
app.include_router(news.router, prefix="/api/news")
app.include_router(analysis.router, prefix="/api")
app.include_router(trading.router, prefix="/api/trading")

# 前端构建产物目录（相对于项目根）
FRONTEND_DIST = Path(__file__).resolve().parent / "frontend" / "dist"


@app.get("/api")
def read_root():
    return {"Hello": "World", "docs": "/docs"}


# 仅当存在 dist 时挂载前端静态资源，否则提供占位页
if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="static")
else:
    @app.get("/", response_class=HTMLResponse)
    def index_fallback():
        return HTMLResponse(
            "<!DOCTYPE html><html><head><meta charset='utf-8'><title>A股智能分析系统</title></head>"
            "<body><h1>A股智能分析系统</h1><p>前端未构建，请先执行：<code>cd web/frontend && npm install && npm run build</code></p>"
            "<p><a href='/docs'>API 文档 (Swagger)</a></p></body></html>"
        )

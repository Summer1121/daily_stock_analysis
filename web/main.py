from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from web.api import config, news, analysis, trading

app = FastAPI()

app.include_router(config.router, prefix="/api")
app.include_router(news.router, prefix="/api/news")
app.include_router(analysis.router, prefix="/api")
app.include_router(trading.router, prefix="/api/trading")


@app.get("/api")
def read_root():
    return {"Hello": "World"}

app.mount("/", StaticFiles(directory="web/frontend/dist", html=True), name="static")

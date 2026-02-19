# -*- coding: utf-8 -*-
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List

from search_service import get_search_service, SearchService
from config import get_config

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


async def news_fetch_loop():
    """Periodically fetch news and broadcast to clients"""
    search_service = get_search_service()
    while True:
        config = get_config()
        stock_list = config.stock_list
        # a fake stock name, search_stock_news needs it
        stocks = [{"code": code, "name": code} for code in stock_list]
        results = search_service.batch_search(stocks)
        
        # Convert results to JSON and broadcast
        # The SearchResponse object is not directly JSON serializable
        json_results = {}
        for code, response in results.items():
            json_results[code] = {
                "query": response.query,
                "results": [r.__dict__ for r in response.results],
                "provider": response.provider,
                "success": response.success,
                "error_message": response.error_message,
                "search_time": response.search_time,
            }
        
        await manager.broadcast(json.dumps(json_results))
        await asyncio.sleep(300)  # 5 minutes


@router.on_event("startup")
async def startup_event():
    # This is not the ideal way to run a background task in FastAPI,
    # but for simplicity, we will use this for now.
    # A better approach would be to use a proper background task library like `arq`.
    asyncio.create_task(news_fetch_loop())


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # The loop is now in a background task
            await asyncio.sleep(60)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.get("/news/{stock_code}")
async def get_stock_news(stock_code: str, search_service: SearchService = Depends(get_search_service)):
    """Get news for a specific stock"""
    # a fake stock name, search_stock_news needs it
    response = search_service.search_stock_news(stock_code, stock_code)
    return {
        "query": response.query,
        "results": [r.__dict__ for r in response.results],
        "provider": response.provider,
        "success": response.success,
        "error_message": response.error_message,
        "search_time": response.search_time,
    }

import os
import asyncio
from fastapi import FastAPI

app = FastAPI(title="Trading Bot Service")

@app.get("/")
def health_check():
    """Render ヘルスチェック用エンドポイント"""
    return {"status": "ok", "service": "Trading Bot Manager"}

@app.on_event("startup")
async def startup_event():
    """サービス起動時のトレード監視バックグラウンドタスク"""
    asyncio.create_task(run_trading_loop())

async def run_trading_loop():
    print("=== Trading Bot Loop Started ===")
    while True:
        await asyncio.sleep(10)

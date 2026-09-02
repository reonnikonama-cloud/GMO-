import os
import asyncio
from fastapi import FastAPI
from trader.trader_manager import HybridTraderManager
from trader.common.order_types import TradeSignal, MarketMetrics, TradeStyle, TradeSide

app = FastAPI(title="Trading Bot Service")
trader = HybridTraderManager()

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Hybrid Trader Manager"}

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_trading_loop())

async def run_trading_loop():
    print("=== Trading Bot Manager Online ===")
    
    # スキャルピングのテストシグナル実行
    dummy_signal = TradeSignal(
        pair="USD/JPY",
        style=TradeStyle.SCALPING,
        side=TradeSide.BUY,
        timestamp="2026-09-02 10:00:00",
        entry_price=150.00,
        sl_pips=10.0,
        metrics=MarketMetrics(spread_ratio=1.1, liquidity_score=0.9)
    )
    
    result = trader.process_signal(dummy_signal)
    print("Test Execution Result:", result)
    
    while True:
        await asyncio.sleep(60)

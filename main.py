import os
import asyncio
from fastapi import FastAPI
from trader.trader_manager import HybridTraderManager
from trader.common.order_types import TradeSignal, MarketMetrics, TradeStyle, TradeSide
from trader.common.db import init_db, log_trade, log_system
from trader.common.notifier import DiscordNotifier

app = FastAPI(title="Trading Bot Service")
trader = HybridTraderManager()
notifier = DiscordNotifier()

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Hybrid Trader Manager"}

@app.on_event("startup")
async def startup_event():
    # データベースの初期化
    init_db()
    log_system("INFO", "Database initialized and system startup.", "2026-09-02 10:00:00")
    
    asyncio.create_task(run_trading_loop())

async def run_trading_loop():
    print("=== Trading Bot Manager Online ===")
    
    # テストシグナルの生成
    dummy_signal = TradeSignal(
        pair="USD/JPY",
        style=TradeStyle.SCALPING,
        side=TradeSide.BUY,
        timestamp="2026-09-02 10:00:00",
        entry_price=150.00,
        sl_pips=10.0,
        metrics=MarketMetrics(spread_ratio=1.1, liquidity_score=0.9)
    )
    
    # 取引評価の実行
    result = trader.process_signal(dummy_signal)
    print("Test Execution Result:", result)
    
    # 評価が承認された場合、DBへの保存とDiscordへの通知を実行
    if result.get("approved") and "order_plan" in result:
        order_plan = result["order_plan"]
        log_trade(order_plan)
        await notifier.send_trade_report(order_plan)
    
    while True:
        await asyncio.sleep(60)

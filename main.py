import os
import asyncio
from fastapi import FastAPI
from trader.trader_manager import HybridTraderManager
from trader.common.order_types import TradeSignal, MarketMetrics, TradeStyle, TradeSide
from trader.common.db import init_db, log_trade, log_system
from trader.common.notifier import DiscordNotifier
from trader.common.gmo_public import GMOPublicAPI

app = FastAPI(title="Trading Bot Service")
trader = HybridTraderManager()
notifier = DiscordNotifier()
gmo_public = GMOPublicAPI()

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Hybrid Trader Manager"}

@app.on_event("startup")
async def startup_event():
    init_db()
    log_system("INFO", "Database initialized and system startup.", "2026-09-02 10:00:00")
    asyncio.create_task(run_trading_loop())

async def run_trading_loop():
    print("=== Trading Bot Manager Online ===")
    
    # 1. APIから暗号資産の全銘柄を動的に抽出
    symbols = await gmo_public.get_symbols()
    print(f"[API] Fetched {len(symbols)} symbols from GMO Coin.")
    for s in symbols:
        print(f" - Symbol: {s.get('symbol')} ({s.get('name')})")

    # 2. 代表的な暗号資産（例: BTC_JPY）のリアルタイム価格を取得してテスト
    target_symbol = "BTC_JPY"
    ticker = await gmo_public.get_ticker(target_symbol)
    current_price = float(ticker.get("last", 9000000.0)) if ticker else 9000000.0
    print(f"[Market] {target_symbol} Current Price: {current_price}")

    # 3. 取得した実価格ベースでスキャルピングシグナルを評価
    dummy_signal = TradeSignal(
        pair=target_symbol,
        style=TradeStyle.SCALPING,
        side=TradeSide.BUY,
        timestamp="2026-09-02 10:00:00",
        entry_price=current_price,
        sl_pips=1000.0,
        metrics=MarketMetrics(spread_ratio=1.1, liquidity_score=0.9)
    )
    
    result = trader.process_signal(dummy_signal)
    print("Test Execution Result:", result)
    
    if result.get("approved") and "order_plan" in result:
        order_plan = result["order_plan"]
        log_trade(order_plan)
        await notifier.send_trade_report(order_plan)
    
    while True:
        await asyncio.sleep(60)

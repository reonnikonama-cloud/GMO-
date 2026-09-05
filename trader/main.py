import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks
from trader.common.gmo_public import GmoPublicClient
from trader.common.capital_gate import CapitalGate
from trader.services.paper_trader import PaperTrader
from trader.services.daily_analyzer import DailyAnalyzer
from trader.services.scheduler import TaskScheduler
from trader.services.notifier import DiscordNotifier
from trader.utils.logger import logger

# アプリ起動時に自動スケジューラーを開始するLifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    task_scheduler = TaskScheduler()
    task_scheduler.start()
    yield

app = FastAPI(title="Crypto Trading Bot Engine", version="0.4.0", lifespan=lifespan)
paper_trader = PaperTrader()
daily_analyzer = DailyAnalyzer()

@app.get("/")
async def root():
    mode = await CapitalGate.get_trading_mode()
    return {"status": "ok", "mode": mode, "message": "Crypto Trading Bot Manager is Running with Auto-Scheduler"}

@app.get("/health")
async def health_check():
    ticker = await GmoPublicClient.get_ticker("BTC")
    mode = await CapitalGate.get_trading_mode()
    return {"status": "healthy", "mode": mode, "btc_ticker": ticker.get("data", [])}

@app.post("/analytics/daily-report")
async def trigger_daily_report(current_capital: float = 100000.0):
    report = daily_analyzer.generate_daily_report(current_capital)
    return {"status": "ok", "daily_report": report}

@app.post("/analytics/check-depletion")
async def check_depletion(current_capital: float):
    if current_capital <= 50000.0:
        knowhow = daily_analyzer.analyze_capital_depletion(current_capital)
        return {"status": "alert", "message": "Depletion analysis generated and archived", "knowhow": knowhow}
    return {"status": "ok", "message": "Capital level is normal"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("trader.main:app", host="0.0.0.0", port=10000, reload=True)

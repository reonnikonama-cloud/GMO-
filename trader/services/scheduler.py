import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from trader.services.trading_engine import TradingEngine
from trader.services.daily_analyzer import DailyAnalyzer
from trader.services.notifier import DiscordNotifier
from trader.common.gmo_websocket import GmoWebSocketClient
from trader.common.capital_gate import CapitalGate
from trader.utils.logger import logger

class TaskScheduler:
    """WebSocketリアルタイム受信用ハイブリッドスケジューラー"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone="Asia/Tokyo")
        self.engine = TradingEngine()
        self.daily_analyzer = DailyAnalyzer()
        self.ws_client = GmoWebSocketClient(symbol="BTC")

    def start(self):
        # 1. WebSocketストリーミングをバックグラウンドタスクとして開始
        asyncio.create_task(
            self.ws_client.start_ticker_stream(
                on_tick_callback=self._handle_realtime_tick
            )
        )

        # 2. 毎日 23:55 (JST) に日次バッチレポートを作成して同期
        self.scheduler.add_job(
            self._job_daily_report,
            trigger=CronTrigger(hour=23, minute=55),
            id="job_daily_report",
            replace_existing=True
        )

        self.scheduler.start()
        logger.info("⏰ [SCHEDULER & WEBSOCKET STARTED] Realtime Tick Stream Active | Daily Report: 23:55 JST")

    async def _handle_realtime_tick(self, last_price: float):
        """WebSocketからTick価格を受信した瞬間にエンジンへ通知"""
        try:
            await self.engine.process_tick(current_price=last_price, symbol="BTC", pair="BTC_JPY", capital=100000.0)
        except Exception as e:
            logger.error(f"Realtime Tick Handler Error: {e}")

    async def _job_daily_report(self):
        try:
            logger.info("📊 [CRON JOB] Generating daily analysis report...")
            mode = await CapitalGate.get_trading_mode()
            report = self.daily_analyzer.generate_daily_report(current_capital=100000.0)

            msg = (
                f"📅 **【日次取引分析レポート】 ({report['date']})**\n"
                f"・稼働モード: `{mode}`\n"
                f"・本日取引回数: {report['trades_count']}回\n"
                f"・本日損益: **{report['daily_pnl']:,} JPY**\n"
                f"・勝率: {report['win_rate']}%\n"
                f"・平均リスクリワード比: {report['avg_rr']}\n"
                f"・市場環境評価: {report['market_condition']}\n"
                f"・次回アクション: {report['action_item']}"
            )
            await DiscordNotifier.send_message(msg)
        except Exception as e:
            logger.error(f"Scheduler Daily Report Error: {e}")

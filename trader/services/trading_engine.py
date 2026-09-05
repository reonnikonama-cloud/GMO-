import asyncio
import pandas as pd
from datetime import datetime
from trader.common.gmo_public import GmoPublicClient
from trader.common.gmo_private import GmoPrivateClient
from trader.common.capital_gate import CapitalGate
from trader.strategy.atr_ma_structure import TechnicalStrategy
from trader.services.paper_trader import PaperTrader
from trader.services.sheets_sync import SheetsSyncService
from trader.utils.logger import logger

class TradingEngine:
    """WebSocketリアルタイム検知 × REST API安全発注 ハイブリッドエンジン"""

    def __init__(self):
        self.strategy = TechnicalStrategy()
        self.paper_trader = PaperTrader()
        self.sheets_sync = SheetsSyncService()
        self.private_client = GmoPrivateClient()
        self.last_signal = "NEUTRAL"
        self.last_sheet_sync_time = None
        self.price_history = []  # リアルタイムTickデータ保持用

    async def process_tick(self, current_price: float, symbol: str = "BTC", pair: str = "BTC_JPY", capital: float = 100000.0):
        """WebSocketからミリ秒単位で流れてくるTickデータのリアルタイム処理"""
        mode = await CapitalGate.get_trading_mode()

        # Tick価格の履歴を保持（ローソク足計算用）
        self.price_history.append(current_price)
        if len(self.price_history) > 60:
            self.price_history.pop(0)

        # テクニカル分析用のデータフレーム作成
        data = {
            'high': [p * 1.0005 for p in self.price_history],
            'low': [p * 0.9995 for p in self.price_history],
            'close': self.price_history
        }
        df = pd.DataFrame(data)

        # 履歴が不足している場合は計算をスキップ
        if len(df) < 20:
            return

        # 1. リアルタイム・テクニカル分析 ＆ 1.5%リスク注文サイズ算定
        analysis = self.strategy.analyze(pair=pair, df=df, capital=capital)
        current_signal = analysis.get("signal")

        # 2. スプレッドシート同期のインターバル制御（API制限回避）
        now = datetime.now()
        should_sync = (
            current_signal != self.last_signal or 
            self.last_sheet_sync_time is None or 
            (now - self.last_sheet_sync_time).total_seconds() >= 900
        )

        if should_sync:
            self.sheets_sync.sync_analysis_data(analysis_res=analysis, mode=mode)
            self.last_signal = current_signal
            self.last_sheet_sync_time = now

        # 3. シグナル成立時の即時発注判定
        plan = analysis.get("order_plan")
        if plan:
            if mode == "PAPER":
                await self.paper_trader.execute_order_plan(plan, current_capital=capital)
            elif mode == "LIVE":
                logger.info(f"🚀 [LIVE WEBSOCKET TRIGGER] Instant order execution: {plan.side.value} {plan.size} {pair}")
                order_res = await self.private_client.place_order(
                    symbol=symbol,
                    side=plan.side.value,
                    execution_type="MARKET",
                    size=plan.size
                )
                logger.info(f"🚀 [LIVE ORDER RESULT] Response: {order_res}")

import json
import asyncio
import websockets
from typing import Callable, Awaitable
from trader.utils.logger import logger

class GmoWebSocketClient:
    """GMOコイン Public WebSocket リアルタイム価格受信クライアント"""

    WS_PUBLIC_URL = "wss://api.coin.z.com/ws/public/v1"

    def __init__(self, symbol: str = "BTC"):
        self.symbol = symbol
        self.is_running = False

    async def start_ticker_stream(self, on_tick_callback: Callable[[float], Awaitable[None]]):
        """Tickerチャネルに接続し、価格更新ごとにコールバック関数を呼び出す"""
        self.is_running = True
        subscribe_msg = {
            "command": "subscribe",
            "channel": "ticker",
            "symbol": self.symbol
        }

        while self.is_running:
            try:
                async with websockets.connect(self.WS_PUBLIC_URL) as ws:
                    await ws.send(json.dumps(subscribe_msg))
                    logger.info(f"📡 [WEBSOCKET CONNECTED] Listening for {self.symbol} ticks...")

                    async for message in ws:
                        data = json.loads(message)
                        if data.get("channel") == "ticker" and "last" in data:
                            last_price = float(data["last"])
                            # 受信した最新価格をシグナル判定エンジンへ渡す
                            await on_tick_callback(last_price)

            except Exception as e:
                logger.error(f"WebSocket Connection Error: {e}. Reconnecting in 5 seconds...")
                await asyncio.sleep(5)

    def stop(self):
        self.is_running = False

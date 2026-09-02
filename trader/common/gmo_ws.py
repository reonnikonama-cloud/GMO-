import asyncio
import json
import websockets

class GMOPublicWS:
    """GMO Coin Public WebSocket (ミリ秒単位の市場データ受信)"""
    def __init__(self, symbol: str = "BTC_JPY"):
        self.uri = "wss://api.coin.z.com/ws/public/v1"
        self.symbol = symbol

    async def connect_and_listen(self):
        async with websockets.connect(self.uri) as websocket:
            subscribe_msg = {
                "command": "subscribe",
                "channel": "ticker",
                "symbol": self.symbol
            }
            await websocket.send(json.dumps(subscribe_msg))
            print(f"=== GMO WS Subscribed to {self.symbol} Ticker ===")

            try:
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    if "channel" in data and data["channel"] == "ticker":
                        # ここでRust処理用キューやPython側マネージャーにデータを流す
                        last = data.get('last', 'N/A')
                        print(f"[WS Ticker] {data['symbol']} | Last Price: {last}")
            except Exception as e:
                print(f"WS Error: {e}")

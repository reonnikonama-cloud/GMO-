import os
import aiohttp
from typing import Dict, Any

class DiscordNotifier:
    """Discord Webhook による通知管理"""
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")

    async def send_trade_report(self, order_plan: Dict[str, Any]):
        """約定・発注通知の送信"""
        if not self.webhook_url:
            print("[Discord] Webhook URL not set. Skip notification.")
            return

        embed = {
            "title": f"🚀 Trade Executed [{order_plan['style']}]",
            "color": 3066993 if order_plan['side'] == "BUY" else 15158332,
            "fields": [
                {"name": "Pair", "value": order_plan['pair'], "inline": True},
                {"name": "Side", "value": order_plan['side'], "inline": True},
                {"name": "Entry Price", "value": str(order_plan['entry_price']), "inline": True},
                {"name": "Stop Loss", "value": str(order_plan['stop_loss']), "inline": True},
                {"name": "Take Profit", "value": str(order_plan['take_profit']), "inline": True},
                {"name": "RR Ratio", "value": str(order_plan['rr_ratio']), "inline": True}
            ],
            "footer": {"text": f"Timestamp: {order_plan['timestamp']}"}
        }
        
        await self._post({"embeds": [embed]})

    async def send_error_alert(self, error_msg: str):
        """障害・異常発生アラートの送信"""
        if not self.webhook_url:
            return

        payload = {
            "content": f"⚠️ **[SYSTEM ALERT] 障害検知**\n```{error_msg}```"
        }
        await self._post(payload)

    async def _post(self, payload: Dict[str, Any]):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.webhook_url, json=payload) as resp:
                    if resp.status != 204 and resp.status != 200:
                        print(f"[Discord Error] Status: {resp.status}")
            except Exception as e:
                print(f"[Discord Connection Error] {e}")

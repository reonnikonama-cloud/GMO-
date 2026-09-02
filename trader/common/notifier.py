import os
import aiohttp
import asyncio
from typing import Dict, Any

class DiscordNotifier:
    """Discord Webhook による通知管理 (Render共有IP 429制限 対応版)"""
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")

    async def send_trade_report(self, order_plan: Dict[str, Any]):
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
        if not self.webhook_url:
            return
        payload = {"content": f"⚠️ **[SYSTEM ALERT] 障害検知**\n```{error_msg}```"}
        await self._post(payload)

    async def _post(self, payload: Dict[str, Any], max_retries: int = 3):
        async with aiohttp.ClientSession() as session:
            for attempt in range(max_retries):
                try:
                    async with session.post(self.webhook_url, json=payload) as resp:
                        # 成功した場合は即終了
                        if resp.status in (200, 204):
                            return
                        
                        # 429エラーの場合
                        if resp.status == 429:
                            # HTTPヘッダーからリセットまでの秒数を取得 (デフォルト5秒)
                            retry_after = float(
                                resp.headers.get("x-ratelimit-reset-after", 
                                resp.headers.get("retry-after", 5.0))
                            )
                            wait_time = retry_after + 1.0  # 安全のため1秒追加
                            print(f"[Discord] 429 Rate limited. Attempt {attempt+1}/{max_retries}. Waiting {wait_time}s...")
                            await asyncio.sleep(wait_time)
                            continue
                        
                        # その他のエラー
                        print(f"[Discord Error] Unhandled Status: {resp.status}")
                        return
                        
                except Exception as e:
                    print(f"[Discord Connection Error] {e}")
                    await asyncio.sleep(2.0)

import aiohttp
import asyncio
from trader.config import config
from trader.utils.logger import logger

class DiscordNotifier:
    @staticmethod
    async def send_message(content: str) -> bool:
        webhook_url = config.DISCORD_WEBHOOK_URL
        if not webhook_url:
            logger.warning("Discord Webhook URL is not set.")
            return False

        payload = {"content": content}
        async with aiohttp.ClientSession() as session:
            for attempt in range(3):
                async with session.post(webhook_url, json=payload) as resp:
                    if resp.status == 204:
                        return True
                    elif resp.status == 429:  # Rate Limit 制御
                        retry_after = (await resp.json()).get("retry_after", 1000) / 1000.0
                        logger.warning(f"Discord Rate Limit. Retrying in {retry_after}s...")
                        await asyncio.sleep(retry_after)
                    else:
                        logger.error(f"Discord Notify Failed: {resp.status}")
                        break
        return False

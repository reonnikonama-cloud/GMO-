import aiohttp
from typing import Dict, Any, Optional
from trader.config import config
from trader.utils.logger import logger

class GmoPublicClient:
    BASE_URL = f"{config.GMO_API_BASE_URL}/public/v1"

    @classmethod
    async def get_ticker(cls, symbol: Optional[str] = None) -> Dict[str, Any]:
        url = f"{cls.BASE_URL}/ticker"
        params = {"symbol": symbol} if symbol else {}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                data = await resp.json()
                if data.get("status") != 0:
                    logger.error(f"GMO Public API Error: {data}")
                return data

    @classmethod
    async def get_orderbooks(cls, symbol: str) -> Dict[str, Any]:
        url = f"{cls.BASE_URL}/orderbooks"
        params = {"symbol": symbol}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                return await resp.json()

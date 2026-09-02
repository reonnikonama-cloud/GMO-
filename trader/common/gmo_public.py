import aiohttp
from typing import List, Dict, Any

class GMOPublicAPI:
    """GMO Coin Public API から銘柄や市場データを動的に取得"""
    def __init__(self):
        self.base_url = "https://api.coin.z.com/public/v1"

    async def get_symbols(self) -> List[Dict[str, Any]]:
        """取扱銘柄（シンボル）の全リストを抽出"""
        url = f"{self.base_url}/symbols"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("data", [])
                else:
                    print(f"[API Error] Failed to fetch symbols: {resp.status}")
                    return []

    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """指定銘柄の最新レートを取得"""
        url = f"{self.base_url}/ticker?symbol={symbol}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = data.get("data", [])
                    if results:
                        return results[0]
                return {}

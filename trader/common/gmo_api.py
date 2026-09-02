import hmac
import hashlib
import time
import json
import aiohttp
from typing import Dict, Any, Optional

class GMOPrivateAPI:
    """GMO Coin Private API 通信管理 (HMAC-SHA256署名対応)"""
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://api.coin.z.com/private"

    def _generate_sign(self, timestamp: str, method: str, path: str, body: str = "") -> str:
        text = timestamp + method + path + body
        sign = hmac.new(
            bytes(self.secret_key.encode('ascii')),
            bytes(text.encode('ascii')),
            hashlib.sha256
        ).hexdigest()
        return sign

    async def request(self, method: str, path: str, payload: Optional[Dict] = None) -> Dict[Any, Any]:
        timestamp = f"{int(time.time() * 1000)}"
        body_str = json.dumps(payload) if payload else ""
        sign = self._generate_sign(timestamp, method, path, body_str)
        
        headers = {
            "API-KEY": self.api_key,
            "API-TIMESTAMP": timestamp,
            "API-SIGN": sign
        }
        
        async with aiohttp.ClientSession() as session:
            url = self.base_url + path
            if method == "GET":
                async with session.get(url, headers=headers) as res:
                    return await res.json()
            elif method == "POST":
                headers["Content-Type"] = "application/json"
                async with session.post(url, headers=headers, data=body_str) as res:
                    return await res.json()

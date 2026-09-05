import hmac
import hashlib
import time
import json
import aiohttp
from typing import Dict, Any, Optional
from trader.config import config
from trader.utils.logger import logger

class GmoPrivateClient:
    BASE_URL = f"{config.GMO_API_BASE_URL}/private/v1"

    def __init__(self):
        self.api_key = config.GMO_API_KEY
        self.secret_key = config.GMO_SECRET_KEY

    def _generate_headers(self, method: str, path: str, body: str = "") -> Dict[str, str]:
        timestamp = str(int(time.time() * 1000))
        text = timestamp + method + path + body
        sign = hmac.new(
            self.secret_key.encode('utf-8'),
            text.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return {
            "API-KEY": self.api_key,
            "API-TIMESTAMP": timestamp,
            "API-SIGN": sign,
            "Content-Type": "application/json"
        }

    async def get_assets(self) -> Dict[str, Any]:
        path = "/v1/account/assets"
        url = f"{config.GMO_API_BASE_URL}/private{path}"
        headers = self._generate_headers("GET", path)

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                return await resp.json()

    async def place_order(self, symbol: str, side: str, execution_type: str, size: float, price: Optional[float] = None, bypass_capital_gate: bool = False) -> Dict[str, Any]:
        # 10万円到達チェック（bypassフラグがない場合は自動でガード）
        if not bypass_capital_gate:
            from trader.common.capital_gate import CapitalGate
            if not await CapitalGate.check_capital_threshold():
                return {
                    "status": -1,
                    "message": f"Order cancelled: Balance has not reached target capital ({config.MIN_REQUIRED_CAPITAL:,.0f} JPY)"
                }

        path = "/v1/order"
        url = f"{config.GMO_API_BASE_URL}/private{path}"
        req_body = {
            "symbol": symbol,
            "side": side,
            "executionType": execution_type,
            "size": str(size)
        }
        if execution_type == "LIMIT" and price:
            req_body["price"] = str(price)

        body_str = json.dumps(req_body)
        headers = self._generate_headers("POST", path, body_str)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=body_str) as resp:
                res = await resp.json()
                logger.info(f"Order Response: {res}")
                return res

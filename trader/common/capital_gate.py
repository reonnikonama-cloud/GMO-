from trader.config import config
from trader.common.gmo_private import GmoPrivateClient
from trader.utils.logger import logger

class CapitalGate:
    """残高が10万円以上か確認し、LIVE/PAPER モードを自動切替"""

    @staticmethod
    async def get_trading_mode() -> str:
        """APIキー未設定または残高10万円未満の場合は 'PAPER'、条件を満たせば 'LIVE' を返す"""
        if not config.GMO_API_KEY or not config.GMO_SECRET_KEY:
            logger.info("Capital Gate: API credentials not configured. Operating in PAPER mode.")
            return "PAPER"

        client = GmoPrivateClient()
        try:
            assets_res = await client.get_assets()
            if assets_res.get("status") != 0:
                logger.warning("Capital Gate: Failed to fetch assets -> Operating in PAPER mode.")
                return "PAPER"

            jpy_amount = 0.0
            for item in assets_res.get("data", []):
                if item.get("symbol") == "JPY":
                    jpy_amount = float(item.get("amount", 0.0))
                    break

            min_capital = config.MIN_REQUIRED_CAPITAL
            if jpy_amount >= min_capital:
                logger.info(f"Capital Gate PASSED: Current JPY={jpy_amount:,.0f} >= Target={min_capital:,.0f} -> Mode: LIVE")
                return "LIVE"
            else:
                logger.info(
                    f"Capital Gate: Current JPY={jpy_amount:,.0f} < Target={min_capital:,.0f}. "
                    f"Target not reached -> Mode: PAPER (Virtual Execution)"
                )
                return "PAPER"
        except Exception as e:
            logger.error(f"Capital Gate Exception: {e} -> Operating in PAPER mode.")
            return "PAPER"

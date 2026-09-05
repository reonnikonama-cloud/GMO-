import math
from trader.config import config
from trader.utils.logger import logger

class RiskManager:
    """指定数式 (総資金 × 1.5% ÷ |エントリー価格 - 損切り価格|) に基づくポジションサイズ計算エンジン"""

    @staticmethod
    def calculate_safe_position_size(
        capital: float,
        entry_price: float,
        stop_loss: float,
        min_size: float = 0.01,
        precision: int = 4
    ) -> float:
        """
        ポジションサイズ ＝ (総資金 × 1.5%) ÷ |エントリー価格 − 損切り価格|
        """
        price_diff = abs(entry_price - stop_loss)
        if price_diff <= 0:
            logger.error("RiskManager Error: Entry price and Stop Loss price cannot be identical.")
            return 0.0

        # 分子: 総資金 × 許容リスク1.5%
        risk_amount = capital * config.MAX_RISK_PERCENT
        
        # 数式に基づく計算: リスク許容額 ÷ 損切り幅
        calculated_size = risk_amount / price_diff

        # 最小発注単位の指定精度（小数点以下4桁）で切り捨て
        factor = 10 ** precision
        safe_size = math.floor(calculated_size * factor) / factor

        if safe_size < min_size:
            logger.warning(
                f"🛡️ [RISK BLOCKED] Calculated size ({safe_size}) < Minimum lot size ({min_size}). "
                f"Capital: {capital:,.0f} JPY | Risk Amount (1.5%): {risk_amount:,.0f} JPY | SL Diff: {price_diff:,.0f} JPY"
            )
            return 0.0

        logger.info(
            f"🛡️ [RISK CHECK PASSED] Capital: {capital:,.0f} JPY | Risk Amount (1.5%): {risk_amount:,.0f} JPY | "
            f"SL Diff: {price_diff:,.0f} JPY -> Position Size: {safe_size}"
        )
        return safe_size

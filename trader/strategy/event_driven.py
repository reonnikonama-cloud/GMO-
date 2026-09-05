from typing import Dict, Any
from trader.utils.logger import logger

class EventDrivenGate:
    """市況イベント発生時、「見込み獲得利幅 > 往復コスト + スプレッド」の場合のみ発注許可"""

    @staticmethod
    def evaluate_market_event(event_data: Dict[str, Any], estimated_cost_pips: float) -> bool:
        expected_gain_pips = event_data.get("expected_gain_pips", 0.0)

        if expected_gain_pips > estimated_cost_pips * 1.5:
            logger.info(f"Event Gate PASSED: ExpectedGain={expected_gain_pips}pips > Cost={estimated_cost_pips}pips")
            return True
        else:
            logger.warning(f"Event Gate REJECTED: Edge insufficient.")
            return False

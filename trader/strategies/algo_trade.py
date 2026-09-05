from typing import Dict, Any
from trader.utils.logger import logger

class AlgoTradeGate:
    """バックテストで「純利益 > 0」かつ「PF > 1.2」を満たす場合のみ発注許可"""

    @staticmethod
    def evaluate_backtest_results(backtest_summary: Dict[str, Any]) -> bool:
        net_profit = backtest_summary.get("net_profit", 0.0)
        profit_factor = backtest_summary.get("profit_factor", 0.0)

        if net_profit > 0 and profit_factor >= 1.2:
            logger.info(f"Algo Gate PASSED: NetProfit={net_profit}, PF={profit_factor}")
            return True
        else:
            logger.warning(f"Algo Gate REJECTED: NetProfit={net_profit}, PF={profit_factor}")
            return False

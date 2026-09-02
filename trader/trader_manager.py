from typing import Dict, Any, Tuple
from trader.common.order_types import TradeSignal, OrderPlan, TradeStyle, TradeSide

try:
    import rust_scalp_engine
except ImportError:
    rust_scalp_engine = None

class HybridTraderManager:
    def __init__(self, target_win_rate: float = 0.50):
        self.target_win_rate = target_win_rate

    def process_signal(self, signal: TradeSignal) -> Dict[str, Any]:
        if signal.style == TradeStyle.SCALPING:
            return self._process_scalp(signal)
        return self._process_python_strategy(signal)

    def _process_scalp(self, signal: TradeSignal) -> Dict[str, Any]:
        if signal.metrics.spread_ratio > 1.5:
            return {"approved": False, "reason": "Reject [SCALPING]: Spread ratio > 1.5"}
        if signal.metrics.volatility_is_extreme:
            return {"approved": False, "reason": "Reject [SCALPING]: Extreme volatility"}

        rr_ratio = 1.00 + (signal.metrics.liquidity_score * 0.24)
        return self._build_order_plan(signal, rr_ratio)

    def _process_python_strategy(self, signal: TradeSignal) -> Dict[str, Any]:
        metrics = signal.metrics
        style = signal.style

        if style == TradeStyle.DAYTRADING:
            if not metrics.is_major_session or metrics.trend_strength < 0.3:
                return {"approved": False, "reason": "Reject [DAYTRADING]: Session or trend insufficient"}
            rr_ratio = 1.5
        elif style == TradeStyle.SWING:
            if metrics.trend_strength < 0.6:
                return {"approved": False, "reason": "Reject [SWING]: Weak trend"}
            rr_ratio = 2.5
        elif style == TradeStyle.POSITION:
            if metrics.trend_strength < 0.8:
                return {"approved": False, "reason": "Reject [POSITION]: Macro trend insufficient"}
            rr_ratio = 4.0
        else:
            return {"approved": False, "reason": "Unknown style"}

        return self._build_order_plan(signal, rr_ratio)

    def _build_order_plan(self, signal: TradeSignal, rr_ratio: float) -> Dict[str, Any]:
        sl_dist = signal.sl_pips * signal.pip_unit
        tp_dist = sl_dist * rr_ratio

        if signal.side == TradeSide.BUY:
            sl_price = signal.entry_price - sl_dist
            tp_price = signal.entry_price + tp_dist
        else:
            sl_price = signal.entry_price + sl_dist
            tp_price = signal.entry_price - tp_dist

        plan = OrderPlan(
            timestamp=signal.timestamp,
            pair=signal.pair,
            style=signal.style,
            side=signal.side,
            entry_price=signal.entry_price,
            stop_loss=round(sl_price, 3),
            take_profit=round(tp_price, 3),
            rr_ratio=round(rr_ratio, 3)
        )

        return {"approved": True, "reason": "Approved", "order_plan": plan.model_dump()}

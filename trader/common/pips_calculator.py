from typing import Dict, Any
from trader.common.order_types import TradeStyle, TradeSide

class PipsCalculator:
    TICK_SIZES: Dict[str, float] = {
        "BTC_JPY": 1.0,
        "ETH_JPY": 1.0,
        "BCH_JPY": 1.0,
        "LTC_JPY": 1.0,
        "XRP_JPY": 0.001,
        "XLM_JPY": 0.001,
        "ADA_JPY": 0.001,
        "DOT_JPY": 0.1,
        "LINK_JPY": 0.1,
    }
    DEFAULT_TICK_SIZE = 1.0

    TARGET_RR: Dict[TradeStyle, float] = {
        TradeStyle.SCALPING: 1.3,
        TradeStyle.DAY_TRADE: 1.8,
        TradeStyle.SWING_TRADE: 2.5,
        TradeStyle.POSITION_TRADE: 4.0,
    }

    TAKER_FEE_RATE = 0.0005
    MAKER_FEE_RATE = -0.0001
    ESTIMATED_SPREAD_RATE = 0.0002

    @classmethod
    def get_pip_size(cls, pair: str) -> float:
        return cls.TICK_SIZES.get(pair, cls.DEFAULT_TICK_SIZE)

    @classmethod
    def calculate_tp_pips(cls, pair: str, style: TradeStyle, sl_pips: float, entry_price: float, is_maker: bool = True) -> float:
        target_rr = cls.TARGET_RR.get(style, 1.0)
        pip_size = cls.get_pip_size(pair)
        raw_tp_pips = sl_pips * target_rr

        if style == TradeStyle.SCALPING:
            fee_rate = cls.MAKER_FEE_RATE if is_maker else cls.TAKER_FEE_RATE
            total_cost_price = entry_price * (fee_rate * 2 + cls.ESTIMATED_SPREAD_RATE)
            cost_pips = total_cost_price / pip_size
            return round(raw_tp_pips + cost_pips, 2)

        return round(raw_tp_pips, 2)

    @classmethod
    def get_execution_plan(cls, pair: str, style: TradeStyle, side: TradeSide, entry_price: float, sl_pips: float, is_maker: bool = True) -> Dict[str, Any]:
        pip_size = cls.get_pip_size(pair)
        tp_pips = cls.calculate_tp_pips(pair, style, sl_pips, entry_price, is_maker)

        sl_diff = sl_pips * pip_size
        tp_diff = tp_pips * pip_size

        if side == TradeSide.BUY:
            sl_price = entry_price - sl_diff
            tp_price = entry_price + tp_diff
        else:
            sl_price = entry_price + sl_diff
            tp_price = entry_price - tp_diff

        return {
            "pair": pair,
            "style": style.value,
            "side": side.value,
            "entry_price": entry_price,
            "sl_pips": sl_pips,
            "tp_pips": tp_pips,
            "stop_loss_price": round(sl_price, 4),
            "take_profit_price": round(tp_price, 4),
            "effective_rr_ratio": round(tp_pips / sl_pips, 2),
            "pip_size": pip_size
        }

from trader.common.order_types import TradeStyle, TradeSide, OrderPlan
from trader.common.pips_calculator import PipsCalculator

class BaseStrategies:
    @staticmethod
    def plan_scalping(pair: str, side: TradeSide, entry_price: float, sl_pips: float) -> OrderPlan:
        plan = PipsCalculator.get_execution_plan(pair, TradeStyle.SCALPING, side, entry_price, sl_pips)
        return OrderPlan(
            pair=pair, style=TradeStyle.SCALPING, side=side,
            entry_price=entry_price, stop_loss=plan["stop_loss_price"],
            take_profit=plan["take_profit_price"], size=0.0, rr_ratio=plan["effective_rr_ratio"]
        )

    @staticmethod
    def plan_day_trade(pair: str, side: TradeSide, entry_price: float, atr_pips: float) -> OrderPlan:
        plan = PipsCalculator.get_execution_plan(pair, TradeStyle.DAY_TRADE, side, entry_price, atr_pips)
        return OrderPlan(
            pair=pair, style=TradeStyle.DAY_TRADE, side=side,
            entry_price=entry_price, stop_loss=plan["stop_loss_price"],
            take_profit=plan["take_profit_price"], size=0.0, rr_ratio=plan["effective_rr_ratio"]
        )

    @staticmethod
    def plan_swing_trade(pair: str, side: TradeSide, entry_price: float, sl_pips: float) -> OrderPlan:
        plan = PipsCalculator.get_execution_plan(pair, TradeStyle.SWING_TRADE, side, entry_price, sl_pips)
        return OrderPlan(
            pair=pair, style=TradeStyle.SWING_TRADE, side=side,
            entry_price=entry_price, stop_loss=plan["stop_loss_price"],
            take_profit=plan["take_profit_price"], size=0.0, rr_ratio=plan["effective_rr_ratio"]
        )

    @staticmethod
    def plan_position_trade(pair: str, side: TradeSide, entry_price: float, sl_pips: float) -> OrderPlan:
        plan = PipsCalculator.get_execution_plan(pair, TradeStyle.POSITION_TRADE, side, entry_price, sl_pips)
        return OrderPlan(
            pair=pair, style=TradeStyle.POSITION_TRADE, side=side,
            entry_price=entry_price, stop_loss=plan["stop_loss_price"],
            take_profit=plan["take_profit_price"], size=0.0, rr_ratio=plan["effective_rr_ratio"],
            use_trailing_stop=True, trailing_step=sl_pips * 0.5 * plan["pip_size"]
        )

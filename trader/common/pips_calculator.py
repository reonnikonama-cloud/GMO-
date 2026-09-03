from enum import Enum
from typing import Dict, Any, Tuple

class TradeStyle(Enum):
    SCALPING = "SCALPING"
    DAY_TRADE = "DAY_TRADE"
    SWING_TRADE = "SWING_TRADE"
    POSITION_TRADE = "POSITION_TRADE"

class TradeSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class PipsCalculator:
    """銘柄ごとのPip定義および目標リスクリワード比に基づくTP/SL Pips算出クラス"""

    # 銘柄ごとの 1 Pip あたりの最小価格刻み（Tick Size）
    TICK_SIZES: Dict[str, float] = {
        "BTC_JPY": 1.0,      # 1 Pip = 1円
        "ETH_JPY": 1.0,      # 1 Pip = 1円
        "BCH_JPY": 1.0,      # 1 Pip = 1円
        "LTC_JPY": 1.0,      # 1 Pip = 1円
        "XRP_JPY": 0.001,    # 1 Pip = 0.001円
        "XLM_JPY": 0.001,    # 1 Pip = 0.001円
        "ADA_JPY": 0.001,    # 1 Pip = 0.001円
        "DOT_JPY": 0.1,      # 1 Pip = 0.1円
        "LINK_JPY": 0.1,     # 1 Pip = 0.1円
    }
    DEFAULT_TICK_SIZE = 1.0

    # スタイル別目標リスクリワード比（RR Ratio）
    TARGET_RR: Dict[TradeStyle, float] = {
        TradeStyle.SCALPING: 1.3,
        TradeStyle.DAY_TRADE: 1.8,
        TradeStyle.SWING_TRADE: 2.5,
        TradeStyle.POSITION_TRADE: 4.0,
    }

    # GMOコイン 手数料率 & 想定スプレッド率
    TAKER_FEE_RATE = 0.0005    # Taker: 0.05%
    MAKER_FEE_RATE = -0.0001   # Maker: -0.01% (リベート)
    ESTIMATED_SPREAD_RATE = 0.0002 # スプレッド 0.02%

    @classmethod
    def get_pip_size(cls, pair: str) -> float:
        """銘柄の1 Pip相当の価格刻みを取得"""
        return cls.TICK_SIZES.get(pair, cls.DEFAULT_TICK_SIZE)

    @classmethod
    def pips_to_price_diff(cls, pair: str, pips: float) -> float:
        """Pipsを実際の価格幅に変換"""
        return pips * cls.get_pip_size(pair)

    @classmethod
    def price_diff_to_pips(cls, pair: str, price_diff: float) -> float:
        """価格幅をPipsに変換"""
        pip_size = cls.get_pip_size(pair)
        return round(price_diff / pip_size, 2)

    @classmethod
    def calculate_tp_pips(
        cls,
        pair: str,
        style: TradeStyle,
        sl_pips: float,
        entry_price: float,
        is_maker: bool = True
    ) -> float:
        """SL pips と 目標RR比から必要な TP pips を算出"""
        target_rr = cls.TARGET_RR.get(style, 1.0)
        pip_size = cls.get_pip_size(pair)
        
        # 基本の TP pips
        raw_tp_pips = sl_pips * target_rr

        # スキャルピングの場合のみ、手数料・スプレッドコストをTP幅に補正加算
        if style == TradeStyle.SCALPING:
            fee_rate = cls.MAKER_FEE_RATE if is_maker else cls.TAKER_FEE_RATE
            total_cost_price = entry_price * (fee_rate * 2 + cls.ESTIMATED_SPREAD_RATE)
            cost_pips = total_cost_price / pip_size
            adjusted_tp_pips = raw_tp_pips + cost_pips
            return round(adjusted_tp_pips, 2)

        return round(raw_tp_pips, 2)

    @classmethod
    def get_execution_plan(
        cls,
        pair: str,
        style: TradeStyle,
        side: TradeSide,
        entry_price: float,
        sl_pips: float,
        is_maker: bool = True
    ) -> Dict[str, Any]:
        """各種パラメータから目標pipsおよび具体的な決済価格（TP/SL）を一元算出"""
        pip_size = cls.get_pip_size(pair)
        tp_pips = cls.calculate_tp_pips(pair, style, sl_pips, entry_price, is_maker)

        sl_price_diff = sl_pips * pip_size
        tp_price_diff = tp_pips * pip_size

        if side == TradeSide.BUY:
            sl_price = entry_price - sl_price_diff
            tp_price = entry_price + tp_price_diff
        else:
            sl_price = entry_price + sl_price_diff
            tp_price = entry_price - tp_price_diff

        actual_rr = round(tp_pips / sl_pips, 2)

        return {
            "pair": pair,
            "style": style.value,
            "side": side.value,
            "entry_price": entry_price,
            "sl_pips": sl_pips,
            "tp_pips": tp_pips,
            "stop_loss_price": round(sl_price, 4),
            "take_profit_price": round(tp_price, 4),
            "effective_rr_ratio": actual_rr,
            "pip_size": pip_size
        }

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional

class TradeStyle(Enum):
    SCALPING = "SCALPING"
    DAY_TRADE = "DAY_TRADE"
    SWING_TRADE = "SWING_TRADE"
    POSITION_TRADE = "POSITION_TRADE"

class TradeSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

@dataclass
class OrderPlan:
    pair: str
    style: TradeStyle
    side: TradeSide
    entry_price: float
    stop_loss: float
    take_profit: float
    size: float
    rr_ratio: float
    use_trailing_stop: bool = False
    trailing_step: Optional[float] = None

class StrategyCalculator:
    """各トレードスタイルの目標リスクリワードに基づくTP/SL算出クラス"""

    # GMOコインの手数料（Taker: 0.05%, Maker: -0.01%）および想定スプレッド率
    TAKER_FEE_RATE = 0.0005
    MAKER_FEE_RATE = -0.0001
    ESTIMATED_SPREAD_RATE = 0.0002

    @classmethod
    def calculate_scalping(cls, pair: str, side: TradeSide, entry_price: float, sl_pips: float, is_maker: bool = True) -> OrderPlan:
        """スキャルピング (目標 RR 1 : 1.3)
        手数料・スプレッドの取引コストをTP幅に補正加算して確実に1.3を確保
        """
        fee_rate = cls.MAKER_FEE_RATE if is_maker else cls.TAKER_FEE_RATE
        cost_per_unit = entry_price * (fee_rate * 2 + cls.ESTIMATED_SPREAD_RATE) # 往復コスト
        
        raw_sl_dist = sl_pips
        target_rr = 1.3
        raw_tp_dist = (raw_sl_dist * target_rr) + cost_per_unit # コスト分をTP幅に上乗せ

        if side == TradeSide.BUY:
            sl = entry_price - raw_sl_dist
            tp = entry_price + raw_tp_dist
        else:
            sl = entry_price + raw_sl_dist
            tp = entry_price - raw_tp_dist

        actual_rr = round(raw_tp_dist / raw_sl_dist, 2)
        return OrderPlan(
            pair=pair, style=TradeStyle.SCALPING, side=side,
            entry_price=entry_price, stop_loss=round(sl, 3), take_profit=round(tp, 3),
            size=0.0, rr_ratio=actual_rr
        )

    @classmethod
    def calculate_day_trade(cls, pair: str, side: TradeSide, entry_price: float, atr: float) -> OrderPlan:
        """デイトレード (目標 RR 1 : 1.8)
        ATR（ボラティリティ）をベースにSLを設定し1.8倍のTPを追従
        """
        target_rr = 1.8
        sl_dist = atr * 1.0  # 1.0 ATRを損切り幅
        tp_dist = sl_dist * target_rr

        if side == TradeSide.BUY:
            sl = entry_price - sl_dist
            tp = entry_price + tp_dist
        else:
            sl = entry_price + sl_dist
            tp = entry_price - tp_dist

        return OrderPlan(
            pair=pair, style=TradeStyle.DAY_TRADE, side=side,
            entry_price=entry_price, stop_loss=round(sl, 3), take_profit=round(tp, 3),
            size=0.0, rr_ratio=target_rr
        )

    @classmethod
    def calculate_swing_trade(cls, pair: str, side: TradeSide, entry_price: float, key_level_sl: float) -> OrderPlan:
        """スイングトレード (目標 RR 1 : 2.5)
        主要サポレジライン（高安値）をSLラインとし、2.5倍の利確幅を自動設定
        """
        target_rr = 2.5
        sl_dist = abs(entry_price - key_level_sl)
        tp_dist = sl_dist * target_rr

        tp = entry_price + tp_dist if side == TradeSide.BUY else entry_price - tp_dist

        return OrderPlan(
            pair=pair, style=TradeStyle.SWING_TRADE, side=side,
            entry_price=entry_price, stop_loss=round(key_level_sl, 3), take_profit=round(tp, 3),
            size=0.0, rr_ratio=target_rr
        )

    @classmethod
    def calculate_position_trade(cls, pair: str, side: TradeSide, entry_price: float, key_level_sl: float) -> OrderPlan:
        """ポジショントレード (目標 RR 1 : 4.0〜 可変)
        初期RR 1:4で設定し、一定利益到達後はトレーリングストップ（追尾決済）へ移行
        """
        initial_rr = 4.0
        sl_dist = abs(entry_price - key_level_sl)
        tp_dist = sl_dist * initial_rr

        tp = entry_price + tp_dist if side == TradeSide.BUY else entry_price - tp_dist
        trailing_step = sl_dist * 0.5  # SL幅の半分単位で追尾

        return OrderPlan(
            pair=pair, style=TradeStyle.POSITION_TRADE, side=side,
            entry_price=entry_price, stop_loss=round(key_level_sl, 3), take_profit=round(tp, 3),
            size=0.0, rr_ratio=initial_rr, use_trailing_stop=True, trailing_step=round(trailing_step, 3)
        )

from dataclasses import dataclass
from enum import Enum
from typing import Optional

class TradeStyle(Enum):
    SCALPING = "SCALPING"
    DAY_TRADE = "DAY_TRADE"
    SWING_TRADE = "SWING_TRADE"
    POSITION_TRADE = "POSITION_TRADE"
    ALGO_TRADE = "ALGO_TRADE"
    EVENT_DRIVEN = "EVENT_DRIVEN"

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

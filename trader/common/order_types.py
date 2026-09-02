from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class TradeStyle(str, Enum):
    SCALPING = "SCALPING"
    DAYTRADING = "DAYTRADING"
    SWING = "SWING"
    POSITION = "POSITION"

class TradeSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class MarketMetrics(BaseModel):
    spread_ratio: float = Field(default=1.0, description="基準スプレッドに対する倍率")
    volatility_is_extreme: bool = Field(default=False, description="超高ボラティリティフラグ")
    trend_strength: float = Field(default=0.5, ge=0.0, le=1.0, description="トレンド強度 (0.0~1.0)")
    is_major_session: bool = Field(default=True, description="主要市場セッション時間帯かどうか")
    liquidity_score: float = Field(default=0.8, ge=0.0, le=1.0, description="流動性スコア")

class TradeSignal(BaseModel):
    pair: str
    style: TradeStyle
    side: TradeSide
    timestamp: str
    entry_price: float
    sl_pips: float
    pip_unit: float = 0.01
    metrics: MarketMetrics

class OrderPlan(BaseModel):
    timestamp: str
    pair: str
    style: TradeStyle
    side: TradeSide
    entry_price: float
    stop_loss: float
    take_profit: float
    rr_ratio: float
    status: str = "APPROVED"

import asyncio
from typing import Dict, Any, List
from trader.common.db import Database
from trader.common.gmo_public import GmoPublicClient
from trader.common.order_types import OrderPlan, TradeSide
from trader.common.risk_manager import RiskManager
from trader.config import config
from trader.utils.logger import logger

class PaperTrader:
    """実際の市場気配値を用いて仮想注文を執行し、2%リスク管理を適用するシミュレーター"""

    def __init__(self):
        self.db = Database()
        self.active_positions: List[Dict[str, Any]] = []

    async def execute_order_plan(self, plan: OrderPlan, current_capital: float = 100000.0) -> Dict[str, Any]:
        """純資産の2%ルールで数量を自動補正・判定後に仮想エントリー"""
        
        # SL幅に基づき、損失2%以内に抑える安全サイズを計算
        safe_size = RiskManager.calculate_safe_position_size(
            capital=current_capital,
            entry_price=plan.entry_price,
            stop_loss=plan.stop_loss
        )

        if safe_size <= 0:
            return {
                "status": -1,
                "message": f"Order rejected by RiskManager: Loss would exceed 2% limit of capital ({current_capital:,.0f} JPY)"
            }

        trade_data = {
            "pair": plan.pair,
            "style": plan.style.value,
            "side": plan.side.value,
            "entry_price": plan.entry_price,
            "stop_loss": plan.stop_loss,
            "take_profit": plan.take_profit,
            "size": safe_size, # 2%ルール適合済みの数量を適用
            "pnl": 0.0,
            "is_paper": True,
            "status": "OPEN",
            "rr_ratio": plan.rr_ratio
        }

        trade_id = self.db.log_trade(trade_data)
        trade_data["id"] = trade_id
        self.active_positions.append(trade_data)

        logger.info(
            f"📝 [PAPER TRADE ENTRY] #{trade_id} {plan.pair} {plan.side.value} | "
            f"Entry: {plan.entry_price} | SL: {plan.stop_loss} | Size: {safe_size} | "
            f"Max Loss at SL: -{(abs(plan.entry_price - plan.stop_loss) * safe_size):,.0f} JPY (<=2%)"
        )
        return {"status": 0, "message": "Paper order executed within 2% risk limit", "trade_id": trade_id, "size": safe_size}

    async def monitor_open_positions(self):
        """リアルタイム価格で利確・損切の到達判定処理"""
        if not self.active_positions:
            return

        for pos in list(self.active_positions):
            symbol = pos["pair"].replace("_JPY", "")
            ticker_res = await GmoPublicClient.get_ticker(symbol)
            
            if ticker_res.get("status") != 0 or not ticker_res.get("data"):
                continue

            ticker_data = ticker_res["data"][0]
            current_bid = float(ticker_data.get("bid", pos["entry_price"]))
            current_ask = float(ticker_data.get("ask", pos["entry_price"]))

            side = pos["side"]
            entry_price = pos["entry_price"]
            stop_loss = pos["stop_loss"]
            take_profit = pos["take_profit"]
            size = pos["size"]
            trade_id = pos["id"]

            is_closed = False
            exit_price = 0.0
            pnl = 0.0

            if side == TradeSide.BUY.value:
                if current_bid >= take_profit:
                    exit_price = take_profit
                    pnl = (exit_price - entry_price) * size
                    is_closed = True
                    logger.info(f"🎯 [PAPER TP HIT] #{trade_id} {pos['pair']} PnL: +{pnl:,.2f} JPY")
                elif current_bid <= stop_loss:
                    exit_price = stop_loss
                    pnl = (exit_price - entry_price) * size
                    is_closed = True
                    logger.info(f"🛑 [PAPER SL HIT] #{trade_id} {pos['pair']} PnL: {pnl:,.2f} JPY")

            elif side == TradeSide.SELL.value:
                if current_ask <= take_profit:
                    exit_price = take_profit
                    pnl = (entry_price - exit_price) * size
                    is_closed = True
                    logger.info(f"🎯 [PAPER TP HIT] #{trade_id} {pos['pair']} PnL: +{pnl:,.2f} JPY")
                elif current_ask >= stop_loss:
                    exit_price = stop_loss
                    pnl = (entry_price - exit_price) * size
                    is_closed = True
                    logger.info(f"🛑 [PAPER SL HIT] #{trade_id} {pos['pair']} PnL: {pnl:,.2f} JPY")

            if is_closed:
                self.db.update_trade_exit(trade_id, exit_price, pnl)
                self.active_positions.remove(pos)

    def get_accumulated_stats(self) -> Dict[str, Any]:
        return self.db.get_paper_stats()

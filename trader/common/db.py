import sqlite3
import os
from typing import Dict, Any, List

class Database:
    def __init__(self, db_path: str = "./data/trader.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trade_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    pair TEXT,
                    style TEXT,
                    side TEXT,
                    entry_price REAL,
                    stop_loss REAL,
                    take_profit REAL,
                    size REAL,
                    pnl REAL,
                    is_paper INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'OPEN',
                    exit_price REAL DEFAULT 0.0,
                    rr_ratio REAL DEFAULT 0.0
                )
            """)
            conn.commit()

    def log_trade(self, data: Dict[str, Any]) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO trade_logs (
                    pair, style, side, entry_price, stop_loss, take_profit, size, pnl, is_paper, status, rr_ratio
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("pair"),
                data.get("style"),
                data.get("side"),
                data.get("entry_price"),
                data.get("stop_loss"),
                data.get("take_profit"),
                data.get("size", 0.01),
                data.get("pnl", 0.0),
                1 if data.get("is_paper", True) else 0,
                data.get("status", "OPEN"),
                data.get("rr_ratio", 0.0)
            ))
            conn.commit()
            return cursor.lastrowid

    def update_trade_exit(self, trade_id: int, exit_price: float, pnl: float, status: str = "CLOSED"):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE trade_logs
                SET exit_price = ?, pnl = ?, status = ?
                WHERE id = ?
            """, (exit_price, pnl, status, trade_id))
            conn.commit()

    def get_paper_stats(self) -> Dict[str, Any]:
        """仮想取引の累積理論値（勝率・累計損益等）を取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*), SUM(pnl), AVG(rr_ratio) FROM trade_logs WHERE is_paper = 1 AND status = 'CLOSED'")
            row = cursor.fetchone()
            total_trades = row[0] or 0
            total_pnl = row[1] or 0.0
            avg_rr = row[2] or 0.0

            cursor.execute("SELECT COUNT(*) FROM trade_logs WHERE is_paper = 1 AND status = 'CLOSED' AND pnl > 0")
            win_trades = cursor.fetchone()[0] or 0

            win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0.0
            return {
                "total_trades": total_trades,
                "win_trades": win_trades,
                "win_rate": round(win_rate, 2),
                "total_pnl": round(total_pnl, 2),
                "avg_rr": round(avg_rr, 2)
            }

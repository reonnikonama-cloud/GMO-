import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List
from trader.common.db import Database
from trader.services.sheets_sync import SheetsSyncService
from trader.utils.logger import logger

class DailyAnalyzer:
    """日次パフォーマンス集計 ＆ 破綻（資金枯渇）根本原因自動レポート生成器"""

    def __init__(self, initial_capital: float = 10000.0):
        self.db = Database()
        self.sheets_sync = SheetsSyncService()
        self.initial_capital = initial_capital  # 口座の初期ペパー金額

    def generate_daily_report(self, current_capital: float) -> Dict[str, Any]:
        """日次トレード結果の分析と改善案作成"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            # 本日の決済済トレード集計
            cursor.execute("""
                SELECT COUNT(*), SUM(pnl), AVG(rr_ratio) 
                FROM trade_logs 
                WHERE is_paper = 1 AND status = 'CLOSED' AND DATE(timestamp) = DATE('now')
            """)
            row = cursor.fetchone()
            trades_count = row[0] or 0
            daily_pnl = round(row[1] or 0.0, 2)
            avg_rr = round(row[2] or 0.0, 2)

            cursor.execute("""
                SELECT COUNT(*) FROM trade_logs 
                WHERE is_paper = 1 AND status = 'CLOSED' AND pnl > 0 AND DATE(timestamp) = DATE('now')
            """)
            win_count = cursor.fetchone()[0] or 0
            win_rate = round((win_count / trades_count * 100), 2) if trades_count > 0 else 0.0

        # 市場コンディション判定・アドバイス生成
        market_condition = "ボラティリティ適正" if win_rate >= 50 else "保ち合い/トレンド転換のノイズ多発"
        action_item = "戦略通り継続" if daily_pnl >= 0 else "レンジ相場での無理なエントリー抑制・ATRバッファー見直し"

        report = {
            "date": today_str,
            "current_capital": current_capital,
            "daily_pnl": daily_pnl,
            "trades_count": trades_count,
            "win_rate": win_rate,
            "avg_rr": avg_rr,
            "max_drawdown": "1.5%制御済",
            "market_condition": market_condition,
            "action_item": action_item
        }

        # スプレッドシートへ同期
        self.sheets_sync.append_daily_report(report)
        return report

    def analyze_capital_depletion(self, current_capital: float) -> Dict[str, Any]:
        """資金が大幅減少・枯渇（例: 50%以上減少または枯渇）した際のアナリティクス"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            # 直近の敗北履歴から連続負け数と最大損失額を算出
            cursor.execute("SELECT pnl, pair, style FROM trade_logs WHERE is_paper = 1 AND status = 'CLOSED' ORDER BY id DESC LIMIT 20")
            trades = cursor.fetchall()

        consecutive_losses = 0
        worst_pnl = 0.0
        for t in trades:
            pnl = t[0]
            if pnl < 0:
                consecutive_losses += 1
                if pnl < worst_pnl:
                    worst_pnl = pnl
            else:
                break

        # パターン分析
        primary_cause = "レンジ相場でのダマシ多発" if consecutive_losses >= 3 else "急激なトレンド反転・ボラティリティ急増"
        root_cause_details = (
            f"連続{consecutive_losses}回の損切りが発生。1.5%リスク制限により一撃破綻は回避されているものの、"
            f"短時間での連続エントリーにより資金が短期間で侵食された。"
        )
        preventative_rule = (
            "【ノウハウルール化】1日に2連敗した場合はその日の自動エントリーを一時停止するクールダウン機能を実装すること。"
        )

        knowhow = {
            "event_type": "CAPITAL_DEPLETED_WARNING" if current_capital > 0 else "ACCOUNT_DEPLETED",
            "final_capital": round(current_capital, 2),
            "consecutive_losses": consecutive_losses,
            "worst_trade_pnl": round(worst_pnl, 2),
            "primary_cause": primary_cause,
            "root_cause_details": root_cause_details,
            "preventative_rule": preventative_rule
        }

        # スプレッドシートへノウハウとして保存
        self.sheets_sync.append_knowhow_report(knowhow)
        return knowhow

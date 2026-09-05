import os
import gspread
from datetime import datetime
from typing import Dict, Any, List
from trader.config import config
from trader.utils.logger import logger

class SheetsSyncService:
    """分析結果・日次レポート・破綻根本原因ノウハウをGoogleスプレッドシートへ出力"""

    def __init__(self):
        self.spreadsheet = None
        self._connect()

    def _connect(self):
        json_path = config.GCP_SERVICE_ACCOUNT_JSON_PATH
        spreadsheet_id = config.GOOGLE_SPREADSHEET_ID

        if not os.path.exists(json_path) or not spreadsheet_id:
            logger.warning("SheetsSyncService: GCP Key or Spreadsheet ID not configured.")
            return

        try:
            client = gspread.service_account(filename=json_path)
            self.spreadsheet = client.open_by_key(spreadsheet_id)
            self._ensure_worksheets()
            logger.info("SheetsSyncService: Successfully connected to Google Sheets.")
        except Exception as e:
            logger.error(f"SheetsSyncService Connection Error: {e}")

    def _ensure_worksheets(self):
        """必要な3つのタブ (リアルタイム、日次分析、ノウハウ蓄積) を初期化"""
        if not self.spreadsheet:
            return

        worksheets = [ws.title for ws in self.spreadsheet.worksheets()]

        # 1. Strategy_Dashboard
        if "Strategy_Dashboard" not in worksheets:
            ws = self.spreadsheet.add_worksheet(title="Strategy_Dashboard", rows="1000", cols="15")
            ws.append_row(["日時", "銘柄", "現在価格", "短期MA", "長期MA", "ATR", "シグナル", "想定Entry", "想定SL", "想定TP", "1.5%許容サイズ", "モード"])

        # 2. Daily_Report (日次分析)
        if "Daily_Report" not in worksheets:
            ws = self.spreadsheet.add_worksheet(title="Daily_Report", rows="1000", cols="10")
            ws.append_row(["日付", "仮想残高", "当日損益(JPY)", "取引回数", "勝率(%)", "平均RR比", "最大ドローダウン", "市場環境評価", "改善アクション"])

        # 3. Knowhow_Archive (資金枯渇・破綻原因アナリティクス)
        if "Knowhow_Archive" not in worksheets:
            ws = self.spreadsheet.add_worksheet(title="Knowhow_Archive", rows="1000", cols="10")
            ws.append_row(["発生日時", "イベント", "最終仮想残高", "連続敗北数", "最大損失トレード", "主因パターン (ボラ/レンジ/トレンド転換)", "根本原因分析", "本番運用の対策・ルール"])

    def sync_analysis_data(self, analysis_res: Dict[str, Any], mode: str):
        if not self.spreadsheet:
            return
        try:
            ws = self.spreadsheet.worksheet("Strategy_Dashboard")
            plan = analysis_res.get("order_plan")
            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                analysis_res.get("pair"),
                analysis_res.get("current_price"),
                analysis_res.get("ma_short"),
                analysis_res.get("ma_long"),
                analysis_res.get("atr"),
                analysis_res.get("signal"),
                plan.entry_price if plan else "-",
                plan.stop_loss if plan else "-",
                plan.take_profit if plan else "-",
                plan.size if plan else 0.0,
                mode
            ]
            ws.append_row(row)
        except Exception as e:
            logger.error(f"SheetsSync Dashboard Error: {e}")

    def append_daily_report(self, report: Dict[str, Any]):
        """日次レポートをスプレッドシートに追記"""
        if not self.spreadsheet:
            return
        try:
            ws = self.spreadsheet.worksheet("Daily_Report")
            row = [
                report.get("date"),
                report.get("current_capital"),
                report.get("daily_pnl"),
                report.get("trades_count"),
                report.get("win_rate"),
                report.get("avg_rr"),
                report.get("max_drawdown"),
                report.get("market_condition"),
                report.get("action_item")
            ]
            ws.append_row(row)
            logger.info(f"📈 [DAILY REPORT SYNCED] Date: {report.get('date')} | Daily PnL: {report.get('daily_pnl')} JPY")
        except Exception as e:
            logger.error(f"SheetsSync Daily Report Error: {e}")

    def append_knowhow_report(self, knowhow: Dict[str, Any]):
        """資金枯渇・破綻時の原因究明レポートをノウハウシートへ永久保存"""
        if not self.spreadsheet:
            return
        try:
            ws = self.spreadsheet.worksheet("Knowhow_Archive")
            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                knowhow.get("event_type", "ACCOUNT_DEPLETED"),
                knowhow.get("final_capital"),
                knowhow.get("consecutive_losses"),
                knowhow.get("worst_trade_pnl"),
                knowhow.get("primary_cause"),
                knowhow.get("root_cause_details"),
                knowhow.get("preventative_rule")
            ]
            ws.append_row(row)
            logger.info(f"🚨 [KNOWHOW ARCHIVED] Depletion Analysis Saved to Google Sheets.")
        except Exception as e:
            logger.error(f"SheetsSync Knowhow Archive Error: {e}")

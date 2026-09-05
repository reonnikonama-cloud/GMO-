import json
from typing import Dict, Any
from trader.config import config
from trader.utils.logger import logger

class GoogleCloudService:
    def __init__(self):
        self.spreadsheet_id = config.GOOGLE_SPREADSHEET_ID
        self.gemini_api_key = config.GEMINI_API_KEY

    async def generate_daily_report_text(self, daily_stats: Dict[str, Any]) -> str:
        """Gemini APIを使用して日次損益報告のテキスト本文を作成"""
        if not self.gemini_api_key:
            return f"【日次レポート】\n本日の損益: {daily_stats.get('total_pnl', 0)} JPY\n勝率: {daily_stats.get('win_rate', 0)}%"

        prompt = f"""
以下の暗号資産自動売買ボットの本日取引結果を分析し、Discord通知用の要約レポートを作成してください。

[取引データ]
- 本日確定損益: {daily_stats.get('total_pnl', 0)} JPY
- 総取引回数: {daily_stats.get('total_trades', 0)} 回
- 勝率: {daily_stats.get('win_rate', 0)} %
- 主なトレードスタイル: {daily_stats.get('primary_style', 'N/A')}

アドバイスや簡単な市況振り返りを含めて簡潔に出力してください。
"""
        # ※ 実運用時は google-genai / google-generativeai SDK を呼出
        return f"🤖 **Gemini AI分析レポート**\n{prompt.strip()}"

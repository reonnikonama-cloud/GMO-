import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GMO_API_KEY: str = os.getenv("GMO_API_KEY", "")
    GMO_SECRET_KEY: str = os.getenv("GMO_SECRET_KEY", "")
    GMO_API_BASE_URL: str = os.getenv("GMO_API_BASE_URL", "https://api.coin.z.com")

    # 資金管理パラメータ
    MIN_REQUIRED_CAPITAL: float = float(os.getenv("MIN_REQUIRED_CAPITAL", "100000.0"))
    MAX_RISK_PERCENT: float = float(os.getenv("MAX_RISK_PERCENT", "0.015"))  # 許容リスク 1.5%

    GCP_SERVICE_ACCOUNT_JSON_PATH: str = os.getenv("GCP_SERVICE_ACCOUNT_JSON_PATH", "./gcp-key.json")
    GOOGLE_SPREADSHEET_ID: str = os.getenv("GOOGLE_SPREADSHEET_ID", "")
    GOOGLE_DRIVE_FOLDER_ID: str = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    DISCORD_WEBHOOK_URL: str = os.getenv("DISCORD_WEBHOOK_URL", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENV: str = os.getenv("ENV", "development")

config = Config()

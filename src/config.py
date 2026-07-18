import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    BOT_NAME = os.getenv("BOT_NAME", "Learning Korean AI v2")
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
    DATABASE_PATH = os.getenv("DATABASE_PATH", "src/database/korean_bot.db")
    PORT = int(os.getenv("PORT", 10000))
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    MODEL_NAME = "gemini-2.5-flash"
    AI_TEMPERATURE = 0.5
    AI_MAX_TOKENS = 1024

    @classmethod
    def validate(cls):
        if not cls.TELEGRAM_TOKEN or not cls.GEMINI_API_KEY:
            raise ValueError("XATOLIK: .env faylida muhim API kalitlar yetishmayapti!")

Config.validate()

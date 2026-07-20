import os

from dotenv import load_dotenv

load_dotenv()


class Config:

    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    BOT_NAME = os.getenv(
        "BOT_NAME",
        "Learning Korean AI"
    )

    MODEL_NAME = "gemini-2.5-flash"

    AI_TEMPERATURE = 0.5

    AI_MAX_TOKENS = 1024

    DATABASE_PATH = "src/database/korean_bot.db"

    @classmethod
    def validate(cls):

        if not cls.TELEGRAM_TOKEN:
            raise ValueError("TELEGRAM_TOKEN topilmadi.")

        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY topilmadi.")


Config.validate()

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from src.config import Config
from src.database import db_client
from src.ai.gemini_client import GeminiClient
from src.handlers.start import start_command
from src.handlers.text_handler import handle_user_text
from src.utils.logger import logger


class KoreanLearningBot:

    def __init__(self):

        self.application = (
            Application.builder()
            .token(Config.TELEGRAM_TOKEN)
            .build()
        )

        self.setup_handlers()

        self.application.post_init = self.on_startup

    def setup_handlers(self):
        """Barcha handlerlarni ulash"""

        self.application.add_handler(
            CommandHandler(
                "start",
                start_command
            )
        )

        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                handle_user_text
            )
        )

        logger.info("Handlerlar muvaffaqiyatli ulandi.")

    async def on_startup(self, app: Application):
        """Bot ishga tushganda bajariladi"""

        logger.info("Database tekshirilmoqda...")

        await db_client.init_db()

        logger.info("Gemini AI yuklanmoqda...")

        app.bot_data["gemini_ai"] = GeminiClient()

        logger.info(f"{Config.BOT_NAME} muvaffaqiyatli ishga tushdi.")

    def run(self):
        """Pollingni boshlash"""

        logger.info("Bot Polling rejimida ishga tushdi.")

        self.application.run_polling(
            drop_pending_updates=True,
            allowed_updates=None,
            close_loop=False,
        )

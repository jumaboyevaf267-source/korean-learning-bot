from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from src.config import Config
from src.database import db_client
from src.ai.gemini_client import GeminiClient
from src.handlers.start import start_command
from src.handlers.language import language_callback
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

        self.application.add_handler(
            CommandHandler("start", start_command)
        )

        self.application.add_handler(
            CallbackQueryHandler(
                language_callback,
                pattern="^lang_"
            )
        )

        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                handle_user_text
            )
        )

        logger.info("Barcha handlerlar muvaffaqiyatli ulandi.")

    async def on_startup(self, app: Application):

        await db_client.init_db()

        app.bot_data["gemini_ai"] = GeminiClient()

        logger.info(f"{Config.BOT_NAME} ishga tushdi.")

    def run(self):

        logger.info("Bot polling rejimida ishga tushmoqda...")

        self.application.run_polling(
            drop_pending_updates=True
        )

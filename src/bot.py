from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
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

        self._register_handlers()

        # Bot ishga tushganda avtomatik bajariladi
        self.application.post_init = self.on_startup

    def _register_handlers(self):
        """Barcha handlerlarni ulash"""

        self.application.add_handler(
            CommandHandler("start", start_command)
        )

        self.application.add_handler(
            CallbackQueryHandler(
                language_callback,
                pattern=r"^lang_"
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
        """Bot ishga tushganda bajariladi"""

        logger.info("Ma'lumotlar bazasi tekshirilmoqda...")

        await db_client.init_db()

        logger.info("Gemini AI yuklanmoqda...")

        app.bot_data["gemini_ai"] = GeminiClient()

        logger.info(f"{Config.BOT_NAME} muvaffaqiyatli ishga tushdi.")

    async def on_shutdown(self, app: Application):
        """Bot to'xtayotganda"""

        logger.info("Bot xavfsiz yopildi.")

    def run(self):
        """Botni Polling rejimida ishga tushirish"""

        logger.info("Bot polling rejimida ishga tushmoqda...")

        self.application.post_shutdown = self.on_shutdown

        self.application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=True,
        )

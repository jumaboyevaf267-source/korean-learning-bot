import asyncio

from telegram import Update
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
from src.handlers.topik import topik_callback
from src.handlers.goal import goal_callback
from src.handlers.menu import menu_callback
from src.handlers.back import back_callback
from src.handlers.vocabulary import vocabulary_callback
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

        self.application.post_init = self.on_startup
        self.application.post_shutdown = self.on_shutdown

    def _register_handlers(self):
        """Barcha handlerlarni ulash"""

        self.application.add_handler(
            CommandHandler(
                "start",
                start_command
            )
        )

        self.application.add_handler(
            CallbackQueryHandler(
                language_callback,
                pattern=r"^lang_"
            )
        )

        self.application.add_handler(
            CallbackQueryHandler(
                topik_callback,
                pattern=r"^topik_"
            )
        )

        self.application.add_handler(
            CallbackQueryHandler(
                goal_callback,
                pattern=r"^goal_"
            )
        )

        self.application.add_handler(
            CallbackQueryHandler(
                menu_callback,
                pattern=r"^menu_"
            )
        )

        self.application.add_handler(
            CallbackQueryHandler(
                vocabulary_callback,
                pattern=r"^vocab_"
            )
        )

        self.application.add_handler(
            CallbackQueryHandler(
                back_callback,
                pattern=r"^back_"
            )
        )

        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                handle_user_text
            )
        )

        logger.info(
            "Barcha handlerlar muvaffaqiyatli ulandi."
        )

    async def on_startup(
        self,
        app: Application
    ):
        """Bot ishga tushganda"""

        logger.info(
            "Database ishga tushirilmoqda..."
        )

        await db_client.init_db()

        logger.info(
            "Gemini AI yuklanmoqda..."
        )

        app.bot_data["gemini_ai"] = GeminiClient()

        logger.info(
            f"{Config.BOT_NAME} muvaffaqiyatli ishga tushdi."
        )

    async def on_shutdown(
        self,
        app: Application
    ):
        """Bot yopilganda"""

        logger.info(
            "Bot xavfsiz yopildi."
        )

    def run(self):
    """Botni ishga tushirish"""

    logger.info(
        "Bot polling rejimida ishga tushmoqda..."
    )

    try:

        self.application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False,
        )

    except (KeyboardInterrupt, SystemExit):

        logger.info(
            "Bot to'xtatildi."
        )

from telegram.ext import Application, CommandHandler, MessageHandler, filters
from src.config import Config
from src.database import db_client
from src.ai.gemini_client import GeminiClient
from src.handlers.start import start_command
from src.handlers.text_handler import handle_user_text
from src.utils.logger import logger

class KoreanLearningBot:
    def __init__(self):
        self.application = Application.builder().token(Config.TELEGRAM_TOKEN).build()
        self.setup_handlers()
        # post_init ni shu yerda ham bog'lash mumkin
        self.application.post_init = self.on_startup

    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", start_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_text))
        logger.info("Bot handlerlari muvaffaqiyatli ulandi.")

    async def on_startup(self, app: Application):
        await db_client.init_db()
        app.bot_data["gemini_ai"] = GeminiClient()
        logger.info(f"{Config.BOT_NAME} tizimi rasman ishga tushdi.")

    # O'zgarish: run funksiyasini async qildik
    async def run(self):
        logger.info("Bot xabarlarni tinglashni boshlamoqda (Polling)...")
        # run_polling o'rniga initialize, start va idle ishlatamiz
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(drop_pending_updates=True)
        # Botni ushlab turish
        await asyncio.Event().wait()
        

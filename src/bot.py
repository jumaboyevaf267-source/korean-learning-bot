import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from src.config import Config
from src.database import db_client
from src.ai.gemini_client import GeminiClient
from src.handlers.start import start_command
from src.handlers.text_handler import handle_user_text
from src.utils.logger import logger

class KoreanLearningBot:
    def __init__(self):
        # Telegram ilovasini token orqali qurish
        self.application = Application.builder().token(Config.TELEGRAM_TOKEN).build()
        self.setup_handlers()
        # Startup funksiyasini yuklash
        self.application.post_init = self.on_startup

    def setup_handlers(self):
        # /start buyrug'ini ulash
        self.application.add_handler(CommandHandler("start", start_command))
        
        # Kelgan barcha matnli xabarlarni AI ga yo'naltirish
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_text))
        
        logger.info("Bot handlerlari muvaffaqiyatli ulandi.")

    async def on_startup(self, app: Application):
        """Bot ishga tushganda bajariladigan amallar"""
        # Ma'lumotlar bazasini har safar tekshirish
        await db_client.init_db()
        
        # AI klientini yaratish
        app.bot_data["gemini_ai"] = GeminiClient()
        
        logger.info(f"{Config.BOT_NAME} tizimi rasman ishga tushdi.")

    async def run(self):
        """Botni poller rejimida ishlatish"""
        logger.info("Bot xabarlarni tinglashni boshlamoqda (Polling)...")
        # Eng barqaror usul: run_polling
        await self.application.run_polling(drop_pending_updates=True)
        

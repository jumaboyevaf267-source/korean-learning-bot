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

    def setup_handlers(self):
        # /start buyrug'ini ulash
        self.application.add_handler(CommandHandler("start", start_command))
        
        # Kelgan barcha matnli xabarlarni AI ga yo'naltirish
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_text))
        
        logger.info("Bot handlerlari muvaffaqiyatli ulandi.")

    async def on_startup(self, app: Application):
        """Bot ishga tushganda bajariladigan amallar"""
        # 1. Ma'lumotlar bazasini tekshirish va jadvallarni yaratish
        await db_client.init_db()
        
        # 2. ChatGPT aytganidek, AI klientini faqat 1 marta yaratib global bot_data ichiga joylaymiz
        app.bot_data["gemini_ai"] = GeminiClient()
        
        logger.info(f"{Config.BOT_NAME} tizimi rasman ishga tushdi.")

    def run(self):
        """Botni poller rejimida ishlatish"""
        # Startup funksiyasini yuklash
        self.application.post_init = self.on_startup
        
        # Botni yoqish
        logger.info("Bot xabarlarni tinglashni boshlamoqda (Polling)...")
        self.application.run_polling(drop_pending_updates=True)

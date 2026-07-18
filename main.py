import asyncio
import sys
from src.bot import KoreanLearningBot
from src.utils.logger import logger

async def main():
    try:
        # Professional bot klassini obyekt sifatida yaratish
        bot = KoreanLearningBot()
        
        # O'zgarish: bot.run() o'rniga application.initialize() ni kutamiz
        # Agar KoreanLearningBot klassingiz ichida 'application' atributi bo'lsa:
        await bot.application.initialize()
        await bot.application.start()
        await bot.application.updater.start_polling()
        
        # Botni ushlab turish
        await asyncio.Event().wait()
        
    except Exception as e:
        logger.critical(f"Botni ishga tushirishda kutilmagan og'ir xatolik: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot tizimi foydalanuvchi tomonidan qo'lda to'xtatildi.")
        

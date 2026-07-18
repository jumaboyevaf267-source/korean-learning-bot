import asyncio
import sys
from src.bot import KoreanLearningBot
from src.utils.logger import logger

async def main():
    """Botning asosiy ishga tushirish funksiyasi."""
    try:
        # Bot klassidan obyekt yaratamiz
        bot = KoreanLearningBot()
        
        # Botni ishga tushiramiz (bot.py dagi async run() funksiyasini kutamiz)
        logger.info("Bot ishga tushirilmoqda...")
        await bot.run()
        
    except Exception as e:
        logger.critical(f"Botni ishga tushirishda kutilmagan og'ir xatolik yuz berdi: {e}")
        # Xatolik yuz bersa, dasturni to'xtatamiz
        sys.exit(1)

if __name__ == "__main__":
    # Windows platformasida asinxron xatoliklarni oldini olish
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    try:
        # Asinxron loopni ishga tushiramiz
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot tizimi foydalanuvchi tomonidan to'xtatildi.")
        

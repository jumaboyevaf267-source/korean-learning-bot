import sys

from src.bot import KoreanLearningBot
from src.utils.logger import logger


def main():
    """Botni ishga tushirish."""

    try:
        logger.info("======================================")
        logger.info("Learning Korean AI Bot ishga tushmoqda...")
        logger.info("======================================")

        bot = KoreanLearningBot()
        bot.run()

    except KeyboardInterrupt:
        logger.info("Bot foydalanuvchi tomonidan to'xtatildi.")

    except Exception as e:
        logger.critical(f"Kutilmagan xatolik: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

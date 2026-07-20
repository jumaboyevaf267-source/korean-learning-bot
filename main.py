import sys

from src.bot import KoreanLearningBot
from src.utils.logger import logger


def main():
    try:
        logger.info("=" * 50)
        logger.info("Learning Korean AI Bot")
        logger.info("Bot ishga tushmoqda...")
        logger.info("=" * 50)

        bot = KoreanLearningBot()

        bot.run()

    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi.")

    except Exception as e:
        logger.critical(f"Kutilmagan xatolik: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

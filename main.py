import sys

from src.bot import KoreanLearningBot
from src.utils.logger import logger


def main():

    try:

        bot = KoreanLearningBot()

        logger.info("Bot ishga tushirilmoqda...")

        bot.run()

    except KeyboardInterrupt:

        logger.info("Bot to'xtatildi.")

    except Exception as e:

        logger.exception(e)

        sys.exit(1)


if __name__ == "__main__":
    main()

import os
import sys
import threading

from flask import Flask

from src.bot import KoreanLearningBot
from src.utils.logger import logger

app = Flask(__name__)


@app.route("/")
def home():
    return "Learning Korean AI Bot is running!"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


def main():
    try:
        threading.Thread(target=run_web, daemon=True).start()

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

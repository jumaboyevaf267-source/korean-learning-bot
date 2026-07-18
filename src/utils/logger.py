import logging
import os
from logging.handlers import RotatingFileHandler
import sys

# Log papkasini yaratish
os.makedirs("logs", exist_ok=True)

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Konsol va cheklangan faylga yozish handlerlari
stream_handler = logging.StreamHandler(sys.stdout)
file_handler = RotatingFileHandler("logs/bot.log", maxBytes=5*1024*1024, backupCount=3, encoding="utf-8") # Maks 5MB

logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[stream_handler, file_handler]
)

logger = logging.getLogger("KoreanLearningBot")

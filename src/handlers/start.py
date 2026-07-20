from telegram import Update

from telegram.ext import ContextTypes

from src.keyboards.language import get_language_keyboard
from src.database import db_client
from src.utils.logger import logger


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    await db_client.add_user(
        user.id,
        user.username if user.username else ""
    )

    text = (
        "👋 Welcome to Learning Korean AI!\n\n"
        "Please choose your language.\n\n"
        "Tilni tanlang.\n"
        "Выберите язык."
    )

    await update.message.reply_text(
        text=text,
        reply_markup=get_language_keyboard()
    )

    logger.info(f"User {user.id} started the bot.")

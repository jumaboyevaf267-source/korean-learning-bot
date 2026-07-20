from telegram import Update
from telegram.ext import ContextTypes

from src.utils.logger import logger


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    language = query.data.replace("lang_", "")

    context.user_data["language"] = language

    if language == "uz":
        text = (
            "🇺🇿 Til o'rnatildi.\n\n"
            "Endi menga istalgan xabar yuboring."
        )

    elif language == "ru":
        text = (
            "🇷🇺 Язык установлен.\n\n"
            "Теперь отправьте мне любое сообщение."
        )

    else:
        text = (
            "🇬🇧 Language selected.\n\n"
            "Now send me any message."
        )

    await query.edit_message_text(text)

    logger.info(f"Language selected: {language}")

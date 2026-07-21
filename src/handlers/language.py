from telegram import Update
from telegram.ext import ContextTypes

from src.keyboards.topik import get_topik_keyboard
from src.keyboards.back import get_back_keyboard
from src.utils.logger import logger


async def language_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    language = query.data.replace(
        "lang_",
        ""
    )

    context.user_data["language"] = language

    if language == "uz":

        text = (
            "🇺🇿 Til o'rnatildi.\n\n"
            "📚 TOPIK darajangizni tanlang."
        )

    elif language == "ru":

        text = (
            "🇷🇺 Язык установлен.\n\n"
            "📚 Выберите ваш уровень TOPIK."
        )

    else:

        text = (
            "🇬🇧 Language selected.\n\n"
            "📚 Choose your TOPIK level."
        )

    keyboard = get_topik_keyboard()

    keyboard.inline_keyboard.append(
        get_back_keyboard("language").inline_keyboard[0]
    )

    await query.edit_message_text(
        text=text,
        reply_markup=keyboard
    )

    logger.info(
        f"Language selected: {language}"
    )

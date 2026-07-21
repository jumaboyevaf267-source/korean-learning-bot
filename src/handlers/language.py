from telegram import Update
from telegram.ext import ContextTypes

from src.keyboards.topik import get_topik_keyboard
from src.utils.logger import logger


async def language_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    language = query.data.replace("lang_", "")

    context.user_data["language"] = language

    context.user_data["page"] = "topik"

    context.user_data["back"] = "language"

    if language == "uz":

        text = (
            "🇺🇿 Til muvaffaqiyatli tanlandi.\n\n"
            "📚 Endi TOPIK darajangizni tanlang."
        )

    elif language == "ru":

        text = (
            "🇷🇺 Язык успешно выбран.\n\n"
            "📚 Теперь выберите ваш уровень TOPIK."
        )

    else:

        text = (
            "🇬🇧 Language selected successfully.\n\n"
            "📚 Now choose your TOPIK level."
        )

    await query.edit_message_text(
        text=text,
        reply_markup=get_topik_keyboard()
    )

    logger.info(
        f"User {query.from_user.id} selected language: {language}"
    )

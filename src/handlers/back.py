from telegram import Update
from telegram.ext import ContextTypes

from src.keyboards.language import get_language_keyboard
from src.keyboards.topik import get_topik_keyboard
from src.keyboards.goal import get_goal_keyboard


async def back_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    language = context.user_data.get("language", "uz")
    page = context.user_data.get("back", "language")

    if page == "language":

        context.user_data["page"] = "language"

        text = (
            "👋 Welcome to Learning Korean AI!\n\n"
            "Please choose your language.\n\n"
            "🇺🇿 Tilni tanlang.\n"
            "🇷🇺 Выберите язык.\n"
            "🇬🇧 Choose your language."
        )

        await query.edit_message_text(
            text=text,
            reply_markup=get_language_keyboard()
        )

        return

    if page == "topik":

        context.user_data["page"] = "topik"
        context.user_data["back"] = "language"

        if language == "uz":

            text = (
                "🇺🇿 Til tanlandi.\n\n"
                "📚 TOPIK darajangizni tanlang."
            )

        elif language == "ru":

            text = (
                "🇷🇺 Язык выбран.\n\n"
                "📚 Выберите уровень TOPIK."
            )

        else:

            text = (
                "🇬🇧 Language selected.\n\n"
                "📚 Choose your TOPIK level."
            )

        await query.edit_message_text(
            text=text,
            reply_markup=get_topik_keyboard()
        )

        return

    if page == "goal":

        context.user_data["page"] = "goal"
        context.user_data["back"] = "topik"

        if language == "uz":

            text = (
                "🎯 O'rganish maqsadingizni tanlang."
            )

        elif language == "ru":

            text = (
                "🎯 Выберите цель обучения."
            )

        else:

            text = (
                "🎯 Choose your learning goal."
            )

        await query.edit_message_text(
            text=text,
            reply_markup=get_goal_keyboard()
            )

from telegram import Update
from telegram.ext import ContextTypes

from src.keyboards.language import get_language_keyboard
from src.keyboards.topik import get_topik_keyboard
from src.keyboards.goal import get_goal_keyboard
from src.keyboards.menu import get_main_menu

from src.utils.logger import logger


async def back_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    destination = query.data.replace(
        "back_",
        ""
    )

    language = context.user_data.get(
        "language",
        "uz"
    )

    if destination == "language":

        text = (
            "👋 Welcome to Learning Korean AI!\n\n"
            "Please choose your language.\n\n"
            "Tilni tanlang.\n"
            "Выберите язык."
        )

        await query.edit_message_text(
            text=text,
            reply_markup=get_language_keyboard()
        )

    elif destination == "topik":

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

        await query.edit_message_text(
            text=text,
            reply_markup=get_topik_keyboard()
        )

    elif destination == "goal":

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

    elif destination == "menu":

        if language == "uz":

            text = (
                "🏠 Asosiy menyu"
            )

        elif language == "ru":

            text = (
                "🏠 Главное меню"
            )

        else:

            text = (
                "🏠 Main Menu"
            )

        await query.edit_message_text(
            text=text,
            reply_markup=get_main_menu(language)
        )

    logger.info(
        f"User {query.from_user.id} returned to {destination}"
            )

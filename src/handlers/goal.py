from telegram import Update
from telegram.ext import ContextTypes

from src.keyboards.menu import get_main_menu
from src.utils.logger import logger


async def goal_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    goal = query.data.replace(
        "goal_",
        ""
    )

    context.user_data["goal"] = goal

    logger.info(
        f"User {query.from_user.id} goal: {goal}"
    )

    language = context.user_data.get(
        "language",
        "uz"
    )

    topik = context.user_data.get(
        "topik",
        "-"
    )

    goal_names = {
        "speaking": "Speaking",
        "vocab": "Vocabulary",
        "grammar": "Grammar",
        "topik": "TOPIK Exam",
        "study": "Study in Korea",
        "work": "Work in Korea",
        "kpop": "K-pop & Drama",
        "travel": "Travel"
    }

    goal_text = goal_names.get(
        goal,
        goal
    )

    if language == "uz":

        text = (
            "🎉 Profilingiz muvaffaqiyatli yaratildi.\n\n"
            f"🌐 Til: O'zbek\n"
            f"📚 TOPIK: {topik}\n"
            f"🎯 Maqsad: {goal_text}\n\n"
            "Quyidagi menyudan foydalanishingiz mumkin."
        )

    elif language == "ru":

        text = (
            "🎉 Ваш профиль успешно создан.\n\n"
            f"🌐 Язык: Русский\n"
            f"📚 TOPIK: {topik}\n"
            f"🎯 Цель: {goal_text}\n\n"
            "Используйте меню ниже."
        )

    else:

        text = (
            "🎉 Your profile has been created successfully.\n\n"
            f"🌐 Language: English\n"
            f"📚 TOPIK: {topik}\n"
            f"🎯 Goal: {goal_text}\n\n"
            "Use the menu below."
        )

    await query.edit_message_text(
        text=text,
        reply_markup=get_main_menu(language)
    )

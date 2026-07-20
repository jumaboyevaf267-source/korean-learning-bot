from telegram import Update
from telegram.ext import ContextTypes

from src.utils.logger import logger


async def goal_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    # Goal ni olish
    goal = query.data.replace("goal_", "")

    # Goal ni vaqtincha saqlash
    context.user_data["goal"] = goal

    logger.info(
        f"User {query.from_user.id} goal: {goal}"
    )

    language = context.user_data.get("language", "uz")
    topik = context.user_data.get("topik", "-")

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

    goal_text = goal_names.get(goal, goal)

    if language == "uz":

        text = (
            "🎉 Ajoyib!\n\n"
            "Profilingiz muvaffaqiyatli yaratildi.\n\n"
            f"🌐 Til: O'zbek\n"
            f"📚 TOPIK: {topik}\n"
            f"🎯 Maqsad: {goal_text}\n\n"
            "🤖 Endi menga istalgan savolni yozishingiz mumkin.\n"
            "Men sizga koreys tilini o'rganishda yordam beraman."
        )

    elif language == "ru":

        text = (
            "🎉 Отлично!\n\n"
            "Ваш профиль успешно создан.\n\n"
            f"🌐 Язык: Русский\n"
            f"📚 TOPIK: {topik}\n"
            f"🎯 Цель: {goal_text}\n\n"
            "🤖 Теперь можете написать мне любое сообщение.\n"
            "Я помогу вам изучать корейский язык."
        )

    else:

        text = (
            "🎉 Great!\n\n"
            "Your profile has been created successfully.\n\n"
            f"🌐 Language: English\n"
            f"📚 TOPIK: {topik}\n"
            f"🎯 Goal: {goal_text}\n\n"
            "🤖 Now send me any message.\n"
            "I'll help you learn Korean."
        )

    await query.edit_message_text(text=text)

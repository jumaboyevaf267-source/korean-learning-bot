from telegram import Update
from telegram.ext import ContextTypes

from src.utils.logger import logger


GOAL_NAMES = {
    "speaking": {
        "uz": "Suhbat",
        "ru": "Разговор",
        "en": "Speaking",
    },
    "vocab": {
        "uz": "Lug'at",
        "ru": "Словарь",
        "en": "Vocabulary",
    },
    "grammar": {
        "uz": "Grammatika",
        "ru": "Грамматика",
        "en": "Grammar",
    },
    "topik": {
        "uz": "TOPIK imtihoni",
        "ru": "Экзамен TOPIK",
        "en": "TOPIK Exam",
    },
    "study": {
        "uz": "Koreyada o'qish",
        "ru": "Учёба в Корее",
        "en": "Study in Korea",
    },
    "work": {
        "uz": "Koreyada ishlash",
        "ru": "Работа в Корее",
        "en": "Work in Korea",
    },
    "travel": {
        "uz": "Sayohat",
        "ru": "Путешествие",
        "en": "Travel",
    },
    "kpop": {
        "uz": "K-pop va Drama",
        "ru": "K-pop и Дорамы",
        "en": "K-pop & Drama",
    },
}


async def goal_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    goal = query.data.replace("goal_", "")

    context.user_data["goal"] = goal

    language = context.user_data.get("language", "uz")

    topik = context.user_data.get("topik", "-")

    logger.info(
        f"User {query.from_user.id} selected goal {goal}"
    )

    goal_name = GOAL_NAMES.get(
        goal,
        {}
    ).get(
        language,
        goal
    )

    if language == "uz":

        text = (
            "🎉 Profilingiz tayyor!\n\n"
            "Quyidagi ma'lumotlar saqlandi:\n\n"
            "🌐 Til: O'zbek\n"
            f"📚 TOPIK: {topik}\n"
            f"🎯 Maqsad: {goal_name}\n\n"
            "🤖 Endi menga istalgan savolni yozishingiz mumkin.\n"
            "Men sizga koreys tilini o'rganishda yordam beraman."
        )

    elif language == "ru":

        text = (
            "🎉 Профиль готов!\n\n"
            "Ваши данные сохранены.\n\n"
            "🌐 Язык: Русский\n"
            f"📚 TOPIK: {topik}\n"
            f"🎯 Цель: {goal_name}\n\n"
            "🤖 Теперь можете написать мне любое сообщение.\n"
            "Я помогу вам изучать корейский язык."
        )

    else:

        text = (
            "🎉 Your profile is ready!\n\n"
            "Your information has been saved.\n\n"
            "🌐 Language: English\n"
            f"📚 TOPIK: {topik}\n"
            f"🎯 Goal: {goal_name}\n\n"
            "🤖 Now send me any message.\n"
            "I'll help you learn Korean."
        )

    await query.edit_message_text(
        text=text
    )

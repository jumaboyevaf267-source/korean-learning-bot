from telegram import Update
from telegram.ext import ContextTypes

from src.utils.logger import logger


async def goal_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    # Callback ma'lumotini olish
    goal = query.data.replace("goal_", "")

    # Vaqtincha foydalanuvchi maqsadini saqlash
    context.user_data["goal"] = goal

    logger.info(
        f"User {query.from_user.id} goal: {goal}"
    )

    language = context.user_data.get("language", "uz")

    if language == "uz":
        text = (
            "🎉 Ajoyib!\n\n"
            "Profilingiz muvaffaqiyatli yaratildi.\n\n"
            "🤖 Endi menga istalgan savolni yozishingiz mumkin.\n"
            "Men sizga koreys tilini o'rganishda yordam beraman."
        )

    elif language == "ru":
        text = (
            "🎉 Отлично!\n\n"
            "Ваш профиль успешно создан.\n\n"
            "🤖 Теперь можете написать мне любое сообщение.\n"
            "Я помогу вам изучать корейский язык."
        )

    else:
        text = (
            "🎉 Great!\n\n"
            "Your profile has been created successfully.\n\n"
            "🤖 Now send me any message.\n"
            "I'll help you learn Korean."
        )

    await query.edit_message_text(text=text)

from telegram import Update
from telegram.ext import ContextTypes

from src.keyboards.goal import get_goal_keyboard
from src.utils.logger import logger


async def topik_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    level = query.data.replace("topik_", "")

    context.user_data["topik"] = level

    context.user_data["page"] = "goal"

    context.user_data["back"] = "topik"

    language = context.user_data.get("language", "uz")

    logger.info(
        f"User {query.from_user.id} selected TOPIK {level}"
    )

    if language == "uz":

        text = (
            f"📚 TOPIK {level} tanlandi.\n\n"
            "🎯 Endi o'rganish maqsadingizni tanlang."
        )

    elif language == "ru":

        text = (
            f"📚 TOPIK {level} выбран.\n\n"
            "🎯 Теперь выберите цель обучения."
        )

    else:

        text = (
            f"📚 TOPIK {level} selected.\n\n"
            "🎯 Choose your learning goal."
        )

    await query.edit_message_text(
        text=text,
        reply_markup=get_goal_keyboard()
    )

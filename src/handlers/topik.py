from telegram import Update
from telegram.ext import ContextTypes

from src.keyboards.goal import get_goal_keyboard
from src.keyboards.back import get_back_keyboard
from src.utils.logger import logger


async def topik_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    level = query.data.replace(
        "topik_",
        ""
    )

    context.user_data["topik"] = level

    logger.info(
        f"User {query.from_user.id} TOPIK level: {level}"
    )

    language = context.user_data.get(
        "language",
        "uz"
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
            "🎯 Now choose your learning goal."
        )

    keyboard = get_goal_keyboard()

    keyboard.inline_keyboard.append(
        get_back_keyboard("topik").inline_keyboard[0]
    )

    await query.edit_message_text(
        text=text,
        reply_markup=keyboard
        )

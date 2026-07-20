from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from src.database import db_client
from src.utils.logger import logger


async def handle_user_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user
    message = update.message.text

    await db_client.add_user(
        user.id,
        user.username if user.username else ""
    )

    await db_client.save_message(
        user.id,
        "user",
        message
    )

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    gemini_ai = context.bot_data.get("gemini_ai")

    if gemini_ai is None:

        logger.error("GeminiClient topilmadi.")

        await update.message.reply_text(
            "⚠️ Server ishga tushmagan."
        )

        return

    history = await db_client.get_history(user.id)

    answer = await gemini_ai.generate_response(
        user.id,
        message,
        history
    )

    await db_client.save_message(
        user.id,
        "model",
        answer
    )

    await update.message.reply_text(answer)

    logger.info(
        f"User {user.id} ga javob yuborildi."
  )

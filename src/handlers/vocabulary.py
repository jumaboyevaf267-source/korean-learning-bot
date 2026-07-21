from telegram import Update
from telegram.ext import ContextTypes

from src.keyboards.vocabulary import get_vocabulary_keyboard


async def vocabulary_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    language = context.user_data.get(
        "language",
        "uz"
    )

    if language == "uz":

        text = (
            "📚 Lug'at\n\n"
            "Quyidagi bo'limlardan birini tanlang."
        )

    elif language == "ru":

        text = (
            "📚 Словарь\n\n"
            "Выберите один из разделов."
        )

    else:

        text = (
            "📚 Vocabulary\n\n"
            "Choose one of the sections below."
        )

    await query.edit_message_text(
        text=text,
        reply_markup=get_vocabulary_keyboard()
    )

from telegram import Update
from telegram.ext import ContextTypes

from src.keyboards.vocabulary import get_vocabulary_keyboard


async def menu_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    data = query.data

    language = context.user_data.get(
        "language",
        "uz"
    )

    if data == "menu_vocab":

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

        return

    if language == "uz":

        text = (
            "🚧 Ushbu bo'lim hali ishlab chiqilmoqda."
        )

    elif language == "ru":

        text = (
            "🚧 Этот раздел пока находится в разработке."
        )

    else:

        text = (
            "🚧 This section is under development."
        )

    await query.answer(
        text=text,
        show_alert=True
    )

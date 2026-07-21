from telegram import Update
from telegram.ext import ContextTypes

from src.utils.logger import logger


async def menu_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    data = query.data.replace("menu_", "")

    language = context.user_data.get(
        "language",
        "uz"
    )

    texts = {

        "uz": {
            "vocab": "📚 Lug'at bo'limi tez orada qo'shiladi.",
            "chat": "💬 AI Chat tayyor. Menga oddiy xabar yozishingiz mumkin.",
            "topik": "📝 TOPIK bo'limi tez orada qo'shiladi.",
            "daily": "🔥 Daily Mission tez orada qo'shiladi.",
            "progress": "📊 Progress tizimi tez orada qo'shiladi.",
            "settings": "⚙️ Sozlamalar tez orada qo'shiladi."
        },

        "ru": {
            "vocab": "📚 Раздел слов скоро появится.",
            "chat": "💬 AI Chat готов. Просто отправьте сообщение.",
            "topik": "📝 Раздел TOPIK скоро появится.",
            "daily": "🔥 Ежедневные задания скоро появятся.",
            "progress": "📊 Статистика скоро появится.",
            "settings": "⚙️ Настройки скоро появятся."
        },

        "en": {
            "vocab": "📚 Vocabulary section coming soon.",
            "chat": "💬 AI Chat is ready. Just send me a message.",
            "topik": "📝 TOPIK section coming soon.",
            "daily": "🔥 Daily Mission coming soon.",
            "progress": "📊 Progress section coming soon.",
            "settings": "⚙️ Settings coming soon."
        }

    }

    await query.answer(
        texts[language][data],
        show_alert=True
    )

    logger.info(
        f"User {query.from_user.id} opened {data}"
    )

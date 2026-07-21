from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_vocabulary_keyboard():

    keyboard = [

        [
            InlineKeyboardButton(
                "🆕 Today's Words",
                callback_data="vocab_today"
            )
        ],

        [
            InlineKeyboardButton(
                "📖 Categories",
                callback_data="vocab_categories"
            )
        ],

        [
            InlineKeyboardButton(
                "🔍 Search Word",
                callback_data="vocab_search"
            )
        ],

        [
            InlineKeyboardButton(
                "⭐ Saved Words",
                callback_data="vocab_saved"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Orqaga",
                callback_data="back_menu"
            )
        ]

    ]

    return InlineKeyboardMarkup(keyboard)

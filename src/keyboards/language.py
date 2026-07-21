from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_language_keyboard():

    keyboard = [

        [
            InlineKeyboardButton(
                "🇺🇿 O'zbekcha",
                callback_data="lang_uz"
            )
        ],

        [
            InlineKeyboardButton(
                "🇷🇺 Русский",
                callback_data="lang_ru"
            )
        ],

        [
            InlineKeyboardButton(
                "🇺🇸 English",
                callback_data="lang_en"
            )
        ]

    ]

    return InlineKeyboardMarkup(keyboard)

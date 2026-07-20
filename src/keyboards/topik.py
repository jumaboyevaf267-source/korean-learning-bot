from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_topik_keyboard():
    """
    Foydalanuvchining TOPIK darajasini tanlash.
    """

    keyboard = [

        [
            InlineKeyboardButton(
                "🌱 Beginner",
                callback_data="topik_0"
            )
        ],

        [
            InlineKeyboardButton(
                "📗 TOPIK 1",
                callback_data="topik_1"
            )
        ],

        [
            InlineKeyboardButton(
                "📘 TOPIK 2",
                callback_data="topik_2"
            )
        ],

        [
            InlineKeyboardButton(
                "📙 TOPIK 3",
                callback_data="topik_3"
            )
        ],

        [
            InlineKeyboardButton(
                "📕 TOPIK 4",
                callback_data="topik_4"
            )
        ],

        [
            InlineKeyboardButton(
                "🏆 TOPIK 5+",
                callback_data="topik_5"
            )
        ]

    ]

    return InlineKeyboardMarkup(keyboard)

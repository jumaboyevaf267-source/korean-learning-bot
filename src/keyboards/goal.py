from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_goal_keyboard():
    """
    Foydalanuvchining asosiy o'rganish maqsadini tanlash.
    """

    keyboard = [

        [
            InlineKeyboardButton(
                "🎓 TOPIK Exam",
                callback_data="goal_topik"
            )
        ],

        [
            InlineKeyboardButton(
                "💬 Daily Conversation",
                callback_data="goal_conversation"
            )
        ],

        [
            InlineKeyboardButton(
                "✈️ Travel",
                callback_data="goal_travel"
            )
        ],

        [
            InlineKeyboardButton(
                "💼 Work",
                callback_data="goal_work"
            )
        ],

        [
            InlineKeyboardButton(
                "📚 Grammar",
                callback_data="goal_grammar"
            )
        ],

        [
            InlineKeyboardButton(
                "🎭 Just for Fun",
                callback_data="goal_fun"
            )
        ]

    ]

    return InlineKeyboardMarkup(keyboard)

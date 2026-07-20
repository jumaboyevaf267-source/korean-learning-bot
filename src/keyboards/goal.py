from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_goal_keyboard():

    keyboard = [

        [
            InlineKeyboardButton(
                "💬 Speaking",
                callback_data="goal_speaking"
            )
        ],

        [
            InlineKeyboardButton(
                "📖 Vocabulary",
                callback_data="goal_vocab"
            )
        ],

        [
            InlineKeyboardButton(
                "📝 Grammar",
                callback_data="goal_grammar"
            )
        ],

        [
            InlineKeyboardButton(
                "🔥 TOPIK Exam",
                callback_data="goal_topik"
            )
        ],

        [
            InlineKeyboardButton(
                "🇰🇷 Study in Korea",
                callback_data="goal_study"
            )
        ],

        [
            InlineKeyboardButton(
                "💼 Work in Korea",
                callback_data="goal_work"
            )
        ],

        [
            InlineKeyboardButton(
                "🎵 K-pop & Drama",
                callback_data="goal_kpop"
            )
        ],

        [
            InlineKeyboardButton(
                "✈️ Travel",
                callback_data="goal_travel"
            )
        ]

    ]

    return InlineKeyboardMarkup(keyboard)

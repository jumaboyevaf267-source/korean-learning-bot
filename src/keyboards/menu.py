from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu(language="uz"):

    if language == "uz":

        keyboard = [

            [
                InlineKeyboardButton(
                    "📚 Lug'at",
                    callback_data="menu_vocab"
                )
            ],

            [
                InlineKeyboardButton(
                    "💬 AI Chat",
                    callback_data="menu_chat"
                )
            ],

            [
                InlineKeyboardButton(
                    "📝 TOPIK",
                    callback_data="menu_topik"
                )
            ],

            [
                InlineKeyboardButton(
                    "🔥 Daily Mission",
                    callback_data="menu_daily"
                )
            ],

            [
                InlineKeyboardButton(
                    "📊 Progress",
                    callback_data="menu_progress"
                )
            ],

            [
                InlineKeyboardButton(
                    "⚙️ Sozlamalar",
                    callback_data="menu_settings"
                )
            ]

        ]

    elif language == "ru":

        keyboard = [

            [
                InlineKeyboardButton(
                    "📚 Слова",
                    callback_data="menu_vocab"
                )
            ],

            [
                InlineKeyboardButton(
                    "💬 AI Chat",
                    callback_data="menu_chat"
                )
            ],

            [
                InlineKeyboardButton(
                    "📝 TOPIK",
                    callback_data="menu_topik"
                )
            ],

            [
                InlineKeyboardButton(
                    "🔥 Ежедневное задание",
                    callback_data="menu_daily"
                )
            ],

            [
                InlineKeyboardButton(
                    "📊 Прогресс",
                    callback_data="menu_progress"
                )
            ],

            [
                InlineKeyboardButton(
                    "⚙️ Настройки",
                    callback_data="menu_settings"
                )
            ]

        ]

    else:

        keyboard = [

            [
                InlineKeyboardButton(
                    "📚 Vocabulary",
                    callback_data="menu_vocab"
                )
            ],

            [
                InlineKeyboardButton(
                    "💬 AI Chat",
                    callback_data="menu_chat"
                )
            ],

            [
                InlineKeyboardButton(
                    "📝 TOPIK",
                    callback_data="menu_topik"
                )
            ],

            [
                InlineKeyboardButton(
                    "🔥 Daily Mission",
                    callback_data="menu_daily"
                )
            ],

            [
                InlineKeyboardButton(
                    "📊 Progress",
                    callback_data="menu_progress"
                )
            ],

            [
                InlineKeyboardButton(
                    "⚙️ Settings",
                    callback_data="menu_settings"
                )
            ]

        ]

    return InlineKeyboardMarkup(keyboard)

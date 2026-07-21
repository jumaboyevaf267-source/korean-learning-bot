from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_back_keyboard(destination: str):

    keyboard = [

        [
            InlineKeyboardButton(
                "⬅️ Orqaga",
                callback_data=f"back_{destination}"
            )
        ]

    ]

    return InlineKeyboardMarkup(keyboard)

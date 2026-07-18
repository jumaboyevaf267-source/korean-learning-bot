from telegram import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu() -> ReplyKeyboardMarkup:
    """Botning asosiy boshqaruv menyusi tugmalari"""
    keyboard = [
        [KeyboardButton("🤖 AI Ustoz (Suhbat)"), KeyboardButton("📝 TOPIK Mashqlar")],
        [KeyboardButton("📊 Mening Statstikam"), KeyboardButton("⚙️ Sozlamalar")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

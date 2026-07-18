from telegram import Update
from telegram.ext import ContextTypes
from src.database import db_client
from src.keyboards.main_menu import get_main_menu
from src.utils.logger import logger

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Foydalanuvchi /start buyrug'ini yuborganda ishga tushadi.
    """
    user = update.effective_user
    
    if not user:
        return

    try:
        # Bazaga qo'shish (await bilan)
        await db_client.add_user(user.id, user.username)
        
        welcome_text = (
            f"안녕하세요, {user.first_name}! 👋\n\n"
            f"Men professional Koreys tili AI o'qituvchisiman. "
            f"Men bilan TOPIK imtihoniga tayyorlanishingiz, koreyscha suhbatlashishingiz "
            f"va grammatikangizni mukammallashtirishingiz mumkin.\n\n"
            f"Boshlash uchun quyidagi menyudan kerakli bo'limni tanlang 👇"
        )
        
        # Xabarni yuborish
        await update.message.reply_text(text=welcome_text, reply_markup=get_main_menu())
        logger.info(f"User {user.id} botni ishga tushirdi (/start).")
        
    except Exception as e:
        logger.error(f"/start buyrug'ini yuborishda xatolik (User: {user.id}): {e}")
        

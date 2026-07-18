from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from src.database import db_client
from src.utils.logger import logger

# GeminiClient obyekti bu yerda emas, bot.py yoki markaziy qismda 
# bir marta yaratilib context.bot_data ichida uzatiladi (Singleton uslubi)

async def handle_user_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_message = update.message.text
    
    await db_client.add_user(user.id, user.username)
    await db_client.save_message(user.id, "user", user_message)
    
    # TODO: Kelajakda prompt uzunligini va tokenlarni nazorat qilish funksiyasini qo'shish
    chat_history = await db_client.get_history(user.id, limit=20)
    logger.info(f"User {user.id} uchun tarixdan {len(chat_history)} ta xabar yuklandi.")
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    
    # Global bot_data ichidan yagona Gemini mijozini olamiz
    gemini_ai = context.bot_data.get("gemini_ai")
    if not gemini_ai:
        logger.error("GeminiClient bot_data ichidan topilmadi!")
        return

    ai_response = await gemini_ai.generate_response(user.id, user_message, chat_history)
    await db_client.save_message(user.id, "model", ai_response)
    
    # Telegram xatoliklarini xavfsiz ushlash (try/except)
    try:
        await update.message.reply_text(ai_response)
        logger.info(f"User {user.id} matniga javob muvaffaqiyatli yetkazildi.")
    except Exception as e:
        logger.error(f"Telegram javob yuborishda xatolik (User: {user.id}): {e}")
      

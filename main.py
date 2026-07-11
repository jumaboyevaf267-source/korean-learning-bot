import os
import telebot
import requests
from flask import Flask, request
import google.generativeai as genai

# --- KONFIGURATSIYA ---
TOKEN = "8859112289:AAFfySswTXD2bX9eX08kshjCOqgFrQ0gl3M"  # Bot tokeningiz
GEMINI_API_KEY = "AQ.Ab8RN6IuNLKPqVN2vU5J-Cf7NiooeVPMK3rZz-NS687ikTb1vA"
RENDER_APP_URL = "https://korean-learning-bot-98d9.onrender.com"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Esbki barqaror kutubxona konfiguratsiyasi
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

user_sessions = {}

# Sifatli va barqaror audio darslar (Ochiq havolalar)
LESSONS = [
    {
        "audio": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", # Buni keyinchalik o'zingizning aniq audio havolangizga almashtirishingiz mumkin
        "text": "우와, 독서 좋아해? 멋지다! 나는 소설도 좋아해.",
        "uz": "Uva, kitob o'qishni yaxshi ko'rasanmi? Ajoyib! Men romanlarni ham yaxshi ko'raman."
    }
]

@app.route('/')
def index():
    return "Bot is active!"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(commands=['start', 'next'])
def start_lesson(message):
    chat_id = message.chat.id
    lesson = LESSONS[0]
    user_sessions[chat_id] = {"text": lesson["text"], "last_analysis": ""}
    
    bot.send_message(chat_id, "🎧 Yangi dars! Quyidagi ovozni eshiting va xuddi shunday ovozli xabar yuboring:")
    
    # Dars audiosini yuborish
    try:
        bot.send_voice(chat_id, lesson["audio"])
    except Exception:
        bot.send_message(chat_id, "⚠️ Dars ovozini yuklashda muammo bo'ldi.")
        
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("📋 Text", callback_data="show_text"),
        telebot.types.InlineKeyboardButton("ℹ️ Help", callback_data="show_help")
    )
    
    bot.send_message(
        chat_id, 
        f"🗣️ {lesson['text']}\n🇺🇿 {lesson['uz']}", 
        reply_markup=markup, 
        parse_mode="Markdown"
    )

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    chat_id = message.chat.id
    if chat_id not in user_sessions:
        bot.send_message(chat_id, "Iltimos, avval /start buyrug'ini bosing.")
        return

    status_msg = bot.send_message(chat_id, "🤔 Ovozli xabaringiz tahlil qilinmoqda...")

    # Telegramdan faylni yuklab olish
    file_info = bot.get_file(message.voice.file_id)
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
    audio_bytes = requests.get(file_url).content
    
    original_text = user_sessions[chat_id]["text"]

    try:
        # Eski kutubxonada audio faylni xatosiz uzatish formati
        audio_part = {
            "mime_type": "audio/ogg",
            "data": audio_bytes
        }
        
        prompt = (
            f"Foydalanuvchi ushbu koreyscha gapni o'qishga harakat qildi: '{original_text}'. "
            f"Uning talaffuzini eshitib, xatolarini juda qisqa va aniq o'zbek tilida tushuntirib ber. "
            f"Oxirida unga 100 balldan baho qo'y."
        )
        
        response = model.generate_content([audio_part, prompt])
        ai_result = response.text
    except Exception as e:
        ai_result = f"Tahlil jarayonida xatolik yuz berdi: {str(e)}"

    user_sessions[chat_id]["last_analysis"] = ai_result
    bot.delete_message(chat_id, status_msg.message_id)

    # Natijani matn va tugmalar orqali chiqarish
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("💡 Explain", callback_data="explain"),
        telebot.types.InlineKeyboardButton("🎯 Score", callback_data="score")
    )
    markup.add(telebot.types.InlineKeyboardButton("➡️ Keyingi dars", callback_data="next_lesson"))

    bot.send_message(chat_id, f"🎙️ **AI Tahlili:**\n\n{ai_result}", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat_id = call.message.chat.id
    if call.data == "next_lesson":
        start_lesson(call.message)
    elif call.data in ["explain", "score"]:
        analysis = user_sessions.get(chat_id, {}).get("last_analysis", "Ma'lumot topilmadi.")
        bot.send_message(chat_id, f"📊 **Batafsil ma'lumot:**\n\n{analysis}")
    elif call.data == "show_text":
        original_text = user_sessions.get(chat_id, {}).get("text", "Matn topilmadi.")
        bot.send_message(chat_id, f"📋 **Dars matni:**\n\n{original_text}")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_APP_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
    

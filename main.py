import os
import telebot
import requests
from flask import Flask, request
from google import genai

# --- KONFIGURATSIYA ---
TOKEN = "8859112289:AAFfySswTXD2bX9eX08kshjCOqgFrQ0gl3M"  # Shaxsiy tokeningizni shu yerga yozing
GEMINI_API_KEY = "AQ.Ab8RN6IuNLKPqVN2vU5J-Cf7NiooeVPMK3rZz-NS687ikTb1vA"
RENDER_APP_URL = "https://korean-learning-bot-98d9.onrender.com"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# Darslar va foydalanuvchi seanslari
user_sessions = {}
LESSONS = [
    {"text": "우와, 독서 좋아해? 멋지다! 나는 소설도 좋아해.", "uz": "Uva, kitob o'qishni yaxshi ko'rasanmi? Ajoyib! Men romanlarni ham yaxshi ko'raman."},
    {"text": "한국어 공부는 재미있지만 조금 어렵습니다.", "uz": "Koreys tilini o'rganish qiziqarli, lekin biroz qiyin."}
]

@app.route('/')
def index():
    return "Bot is running flawlessly!"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(commands=['start', 'next'])
def start_lesson(message):
    import random
    lesson = random.choice(LESSONS)
    user_sessions[message.chat.id] = {"text": lesson["text"], "last_analysis": ""}
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("📋 Text", callback_data="show_text"),
        telebot.types.InlineKeyboardButton("ℹ️ Help", callback_data="show_help")
    )
    
    bot.send_message(
        message.chat.id, 
        f"🎙️ **Koreyscha jumlani ovozli xabar orqali o'qing:**\n\n🗣️ {lesson['text']}\n🇺🇿 {lesson['uz']}", 
        reply_markup=markup, 
        parse_mode="Markdown"
    )

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    chat_id = message.chat.id
    if chat_id not in user_sessions:
        bot.send_message(chat_id, "Iltimos, avval darsni boshlash uchun /start bosing.")
        return

    bot.send_message(chat_id, "🤔 Ovozli xabaringiz tahlil qilinmoqda...")

    # Telegramdan audioni yuklab olish
    file_info = bot.get_file(message.voice.file_id)
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
    audio_data = requests.get(file_url).content
    
    original_text = user_sessions[chat_id]["text"]

    try:
        # Gemini AI yordamida audio tahlili va interaktiv muloqot
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                {"inline_data": {"data": audio_data, "mime_type": "audio/ogg"}},
                f"Ushbu audio foydalanuvchining '{original_text}' gapini o'qishga urinishi. "
                f"Talaffuz xatolarini tuzatib, suhbatni muloqot ko'rinishida davom ettir. "
                f"Javobni aniq o'zbek tilida ber."
            ]
        )
        ai_result = response.text
    except Exception as e:
        ai_result = "Kechirasiz, sun'iy intellekt tahlilida xatolik yuz berdi."

    user_sessions[chat_id]["last_analysis"] = ai_result

    # Skrinshotdagi kabi "Explain" va "Score" tugmalari
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("💡 Explain", callback_data="explain"),
        telebot.types.InlineKeyboardButton("🎯 Score", callback_data="score")
    )
    markup.add(telebot.types.InlineKeyboardButton("➡️ Keyingi dars", callback_data="next_lesson"))

    bot.send_message(chat_id, f"💡 {ai_result}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat_id = call.message.chat.id
    if call.data == "next_lesson":
        start_lesson(call.message)
    elif call.data in ["explain", "score"]:
        analysis = user_sessions.get(chat_id, {}).get("last_analysis", "Ma'lumot topilmadi.")
        bot.send_message(chat_id, f"📊 **Natija:**\n\n{analysis}")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_APP_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
    

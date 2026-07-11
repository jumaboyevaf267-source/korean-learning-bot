import os
import telebot
import requests
from flask import Flask, request
from google import genai

# --- KONFIGURATSIYA ---
TOKEN = "8859112289:AAFfySswTXD2bX9eX08kshjCOqgFrQ0gl3M"  # Shaxsiy bot tokeningiz
GEMINI_API_KEY = "AQ.Ab8RN6IuNLKPqVN2vU5J-Cf7NiooeVPMK3rZz-NS687ikTb1vA"
RENDER_APP_URL = "https://korean-learning-bot-98d9.onrender.com"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
ai_client = genai.Client(api_key=GEMINI_API_KEY)

user_sessions = {}

# Darslar bazasi (Matn ko'rinishida, AI buni avtomatik ovozli qilib beradi)
LESSONS = [
    {
        "text": "우와, 독서 좋아해? 멋지다! 나는 소설도 좋아해.",
        "uz": "Uva, kitob o'qishni yaxshi ko'rasanmi? Ajoyib! Men romanlarni ham yaxshi ko'raman."
    },
    {
        "text": "한국어 공부는 재미있지만 조금 어렵습니다.",
        "uz": "Koreys tilini o'rganish qiziqarli, lekin biroz qiyin."
    },
    {
        "text": "오늘 날씨가 정말 좋네요. 같이 산책할래요?",
        "uz": "Bugun ob-havo juda yaxshi. Birga sayr qilamizmi?"
    }
]

@app.route('/')
def index():
    return "Bot is running perfectly!"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(commands=['start', 'next'])
def start_lesson(message):
    import random
    chat_id = message.chat.id
    lesson = random.choice(LESSONS)
    user_sessions[chat_id] = {"text": lesson["text"], "last_analysis": ""}
    
    bot.send_message(chat_id, "✨ Yangi dars tayyorlanmoqda... Ovoz yuklanmoqda, kuting.")
    
    # 1. Gemini orqali koreyscha matnni audio formatga o'girib, Telegramga yuborish (Text-to-Speech)
    try:
        audio_response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Ushbu koreyscha gapni ona tilida gapiradigan koreys odamdek aniq talaffuz bilan ovozli o'qib ber: {lesson['text']}",
            config={"response_mime_type": "audio/mp3"}
        )
        audio_bytes = audio_response.candidates[0].content.parts[0].inline_data.data
        bot.send_voice(chat_id, audio_bytes, caption="🎧 Koreyscha talaffuzni eshiting")
    except Exception:
        bot.send_message(chat_id, "⚠️ Ovozli talaffuzni yaratishda muammo bo'ldi, lekin dars matni tayyor.")

    # 2. Tugmalarni chiqarish
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("📋 Text", callback_data="show_text"),
        telebot.types.InlineKeyboardButton("ℹ️ Help", callback_data="show_help")
    )
    
    bot.send_message(
        chat_id, 
        f"🗣️ **Talaffuz qiling va audio yuboring:**\n\n{lesson['text']}\n🇺🇿 {lesson['uz']}", 
        reply_markup=markup, 
        parse_mode="Markdown"
    )

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    chat_id = message.chat.id
    if chat_id not in user_sessions:
        bot.send_message(chat_id, "Iltimos, darsni boshlash uchun avval /start bosing.")
        return

    bot.send_message(chat_id, "🤔 Ovozli xabaringiz qabul qilindi, sun'iy intellekt tahlil qilmoqda...")

    # Ovozli faylni yuklab olish
    file_info = bot.get_file(message.voice.file_id)
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
    audio_data = requests.get(file_url).content
    
    original_text = user_sessions[chat_id]["text"]

    try:
        # Sun'iy intellekt talaffuzni tahlil qiladi
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                {"inline_data": {"data": audio_data, "mime_type": "audio/ogg"}},
                f"Foydalanuvchi ushbu gapni o'qidi: '{original_text}'. "
                f"Uning koreyscha talaffuz xatolarini juda qisqa va do'stona o'zbek tilida tushuntir. "
                f"Oxirida unga 100 balldan baho qo'y."
            ]
        )
        ai_result = response.text
    except Exception:
        ai_result = "Koreys tili talaffuzini tekshirishda xatolik yuz berdi."

    user_sessions[chat_id]["last_analysis"] = ai_result

    # 3. Gemini tahlil natijasini OVOZLI XABAR ko'rinishida foydalanuvchiga yuborish
    try:
        ai_voice_response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Ushbu o'zbekcha tahlil matnini muloyim repetitor ohangida ovozli o'qib ber: {ai_result}",
            config={"response_mime_type": "audio/mp3"}
        )
        ai_voice_bytes = ai_voice_response.candidates[0].content.parts[0].inline_data.data
        bot.send_voice(chat_id, ai_voice_bytes, caption="🤖 Oqituvchining ovozli tahlili")
    except Exception:
        bot.send_message(chat_id, f"🎙️ AI Matnli tahlili:\n\n{ai_result}")

    # Tugmalar paneli
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("💡 Explain", callback_data="explain"),
        telebot.types.InlineKeyboardButton("🎯 Score", callback_data="score")
    )
    markup.add(telebot.types.InlineKeyboardButton("➡️ Keyingi dars", callback_data="next_lesson"))

    bot.send_message(chat_id, "📊 Natijalar tayyorlandi. Quyidagi tugmalar orqali batafsil ma'lumot olishingiz mumkin:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat_id = call.message.chat.id
    if call.data == "next_lesson":
        start_lesson(call.message)
    elif call.data == "explain" or call.data == "score":
        analysis = user_sessions.get(chat_id, {}).get("last_analysis", "Tahlil ma'lumotlari mavjud emas.")
        bot.send_message(chat_id, f"📊 **Batafsil ma'lumot:**\n\n{analysis}")
    elif call.data == "show_text":
        original_text = user_sessions.get(chat_id, {}).get("text", "Matn topilmadi.")
        bot.send_message(chat_id, f"📋 **Dars matni:**\n\n{original_text}")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_APP_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
    

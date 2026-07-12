import os
import random
import base64
import telebot
import requests
from flask import Flask, request

# --- KONFIGURATSIYA ---
TOKEN = "8859112289:AAFfySswTXD2bX9eX08kshjCOqgFrQ0gl3M"
GEMINI_API_KEY = "AQ.Ab8RN6IuNLKPqVN2vU5J-Cf7NiooeVPMK3rZz-NS687ikTb1vA"
RENDER_APP_URL = "https://korean-learning-bot-98d9.onrender.com"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_sessions = {}

# DARSLAR BAZASI
LESSONS = [
    {
        "text": "우와, 독서 좋아해? 멋지다! 나는 소설도 좋아해.",
        "translations": {
            "uz": "Uva, kitob o'qishni yaxshi ko'rasanmi? Ajoyib! Men romanlarni ham yaxshi ko'raman.",
            "en": "Wow, do you like reading? Cool! I like novels too.",
            "ru": "Вау, любишь читать? Круто! Я тоже люблю романы.",
            "tr": "Vay, kitap okumayı sever misin? Harika! Ben de romanları severim."
        }
    },
    {
        "text": "한국어 공부는 재미있지만 조금 어렵습니다.",
        "translations": {
            "uz": "Koreys tilini o'rganish qiziqarli, lekin biroz qiyin.",
            "en": "Studying Korean is fun but a bit difficult.",
            "ru": "Изучать корейский язык интересно, но немного сложно.",
            "tr": "Koreyce çalışmak eğlenceli ama biraz zor."
        }
    },
    {
        "text": "오늘 날씨가 너무 좋아서 산책하고 싶어요.",
        "translations": {
            "uz": "Bugun ob-havo juda yaxshi, sayr qilgim kelyapti.",
            "en": "The weather is so nice today, I want to take a walk.",
            "ru": "Сегодня такая хорошая погода, хочется прогуляться.",
            "tr": "Bugün hava çok güzel, yürüyüşe çıkmak istiyorum."
        }
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
    chat_id = message.chat.id
    
    lesson = random.choice(LESSONS)
    if chat_id in user_sessions and len(LESSONS) > 1:
        while lesson["text"] == user_sessions[chat_id].get("text"):
            lesson = random.choice(LESSONS)

    user_sessions[chat_id] = {"text": lesson["text"], "translations": lesson["translations"], "last_analysis": ""}
    
    # 2-rasmdagi kabi faqat "Text" va "Help" tugmalari chiqadi
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("📝 Text", callback_data="choose_lang"),
        telebot.types.InlineKeyboardButton("ℹ️ Help", callback_data="show_help")
    )
    
    try:
        # Google API-larsiz, ochiq manbali bepul TTS orqali koreyscha ovoz yaratish
        tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl=ko&client=tw-ob&q={requests.utils.quote(lesson['text'])}"
        headers = {"User-Agent": "Mozilla/5.0"}
        audio_bytes = requests.get(tts_url, headers=headers).content
        
        # Foydalanuvchiga matn ko'rsatilmaydi, faqat toza audio va tagida tugmalar boradi
        bot.send_voice(
            chat_id, 
            audio_bytes, 
            caption="🎧 Audioni eshiting va xuddi shu gapni ovozli xabar orqali yuboring.", 
            reply_markup=markup
        )
    except Exception:
        bot.send_message(chat_id, "Ovoz yuklashda muammo bo'ldi, tugmani bosib matnni ko'ring:", reply_markup=markup)

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    chat_id = message.chat.id
    if chat_id not in user_sessions:
        bot.send_message(chat_id, "Iltimos, darsni boshlash uchun /start buyrug'ini bosing.")
        return

    status_msg = bot.send_message(chat_id, "💡 Ovozli xabaringiz qabul qilindi, sun'iy intellekt tahlil qilmoqda...")

    file_info = bot.get_file(message.voice.file_id)
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
    audio_bytes = requests.get(file_url).content
    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
    
    original_text = user_sessions[chat_id]["text"]

    # Gemini REST API orqali ovozni to'g'ridan-to'g'ri tahlil qilish (401 xatoliklarsiz xavfsiz yo'l)
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{
                "parts": [
                    {"inlineData": {"mimeType": "audio/ogg", "data": audio_b64}},
                    {"text": f"Foydalanuvchi mana bu koreyscha gapni o'qidi: '{original_text}'. Uning talaffuz xatolarini juda qisqa va tushunarli o'zbek tilida tushuntir va 100 balldan baho ber."}
                ]
            }]
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            ai_result = response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            ai_result = "Koreys tili talaffuzini tekshirishda xatolik yuz berdi."
    except Exception:
        ai_result = "Tizim ulanishida muammo yuz berdi."

    user_sessions[chat_id]["last_analysis"] = ai_result
    bot.delete_message(chat_id, status_msg.message_id)

    # Natija tugmalari (Explain, Score va Keyingi dars)
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("💡 Explain", callback_data="explain"),
        telebot.types.InlineKeyboardButton("🎯 Score", callback_data="score")
    )
    markup.add(telebot.types.InlineKeyboardButton("➡️ Keyingi dars", callback_data="next_lesson"))

    bot.send_message(chat_id, f"📝 **AI Matnli tahlili:**\n\n{ai_result}", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat_id = call.message.chat.id
    
    if call.data == "next_lesson":
        start_lesson(call.message)
        
    elif call.data == "choose_lang":
        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(
            telebot.types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
            telebot.types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
        )
        markup.row(
            telebot.types.InlineKeyboardButton("🇷🇺 Russkiy", callback_data="lang_ru"),
            telebot.types.InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr")
        )
        bot.send_message(chat_id, "Qaysi tildagi matn va tarjimani ko'rmoqchisiz?", reply_markup=markup)
        
    elif call.data.startswith("lang_"):
        lang_code = call.data.split("_")[1]
        session = user_sessions.get(chat_id, {})
        original_text = session.get("text", "")
        translations = session.get("translations", {})
        selected_translation = translations.get(lang_code, "Mavjud emas.")
        
        bot.send_message(chat_id, f"💡 **{original_text}**\n🇺🇿 {selected_translation}")
        
    elif call.data in ["explain", "score"]:
        analysis = user_sessions.get(chat_id, {}).get("last_analysis", "Tahlil topilmadi.")
        bot.send_message(chat_id, f"📋 **Batafsil ma'lumot:**\n\n{analysis}")
        
    elif call.data == "show_help":
        bot.send_message(chat_id, "ℹ️ Yuqoridagi ovozli xabarni eshiting va xuddi shu ohangda o'qib, javob qaytaring.")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_APP_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

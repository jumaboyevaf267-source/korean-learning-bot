import os
import random
import telebot
import requests
from flask import Flask, request
from google import genai
from google.genai import types

# --- KONFIGURATSIYA ---
TOKEN = "8859112289:AAFfySswTXD2bX9eX08kshjCOqgFrQ0gl3M"
GEMINI_API_KEY = "AQ.Ab8RN6IuNLKPqVN2vU5J-Cf7NiooeVPMK3rZz-NS687ikTb1vA"
RENDER_APP_URL = "https://korean-learning-bot-98d9.onrender.com"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
client = genai.Client(api_key=GEMINI_API_KEY)

user_sessions = {}

# BOYITILGAN DARSLAR BAZASI (Endi har gal har xil savol chiqadi)
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
    },
    {
        "text": "지금 몇 시예요? 제가 약속 시간에 늦었어요.",
        "translations": {
            "uz": "Hozir soat necha bo'ldi? Men uchrashuv vaqtiga kechikdim.",
            "en": "What time is it now? I'm late for the appointment.",
            "ru": "Который час? Я опоздал на встречу.",
            "tr": "Saat kaç? Randevuya geç kaldım."
        }
    },
    {
        "text": "맛있는 한국 음식을 추천해 줄 수 있어요?",
        "translations": {
            "uz": "Menga mazali koreys taomlarini tavsiya qila olasizmi?",
            "en": "Can you recommend some delicious Korean food?",
            "ru": "Можете порекомендовать вкусную корейскую еду?",
            "tr": "Lezzetli Kore yemekleri tavsiye edebilir misiniz?"
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
    
    # Har safar avvalgisidan farqli tasodifiy dars tanlash
    lesson = random.choice(LESSONS)
    
    # Agar foydalanuvchi aynan shu darsni boya ko'rgan bo'lsa, boshqasini tanlaydi
    if chat_id in user_sessions and len(LESSONS) > 1:
        while lesson["text"] == user_sessions[chat_id].get("text"):
            lesson = random.choice(LESSONS)

    user_sessions[chat_id] = {"text": lesson["text"], "translations": lesson["translations"], "last_analysis": ""}
    
    status_msg = bot.send_message(chat_id, "🎧 Yangi dars audiosi tayyorlanmoqda...")
    
    try:
        # Gemini orqali matnni koreyscha toza ovozga o'girish
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Ushbu koreyscha gapni ona tilida gapiradigan odamdek aniq va tabiiy ohangda o'qib ber: {lesson['text']}",
            config=types.GenerateContentConfig(
                response_mime_type="audio/mp3"
            )
        )
        audio_bytes = response.candidates[0].content.parts[0].inline_data.data
        
        # Yashirin tarjima va yordam tugmalari
        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(
            telebot.types.InlineKeyboardButton("📋 Text & Translation", callback_data="choose_lang"),
            telebot.types.InlineKeyboardButton("ℹ️ Help", callback_data="show_help")
        )
        
        bot.send_voice(
            chat_id, 
            audio_bytes, 
            caption="🗣️ Audioni eshiting va xuddi shu gapni ovozli xabar (voice) orqali qaytarib yuboring.", 
            reply_markup=markup
        )
        bot.delete_message(chat_id, status_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"⚠️ Ovoz yuklashda xato: {str(e)}. Qaytadan urinish: /start", chat_id, status_msg.message_id)

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    chat_id = message.chat.id
    if chat_id not in user_sessions:
        bot.send_message(chat_id, "Iltimos, darsni boshlash uchun /start buyrug'ini bosing.")
        return

    status_msg = bot.send_message(chat_id, "🤔 Ovozli xabaringiz tahlil qilinmoqda...")

    file_info = bot.get_file(message.voice.file_id)
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
    audio_bytes = requests.get(file_url).content
    
    original_text = user_sessions[chat_id]["text"]

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(data=audio_bytes, mime_type='audio/ogg'),
                f"Foydalanuvchi mana bu gapni o'qidi: '{original_text}'. Uning talaffuz xatolarini juda qisqa va tushunarli o'zbek tilida tushuntir va 100 balldan baho ber."
            ]
        )
        ai_result = response.text
    except Exception as e:
        ai_result = f"Tahlilda xato: {str(e)}"

    user_sessions[chat_id]["last_analysis"] = ai_result
    bot.delete_message(chat_id, status_msg.message_id)

    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("💡 Explain", callback_data="explain"),
        telebot.types.InlineKeyboardButton("🎯 Score", callback_data="score")
    )
    markup.add(telebot.types.InlineKeyboardButton("➡️ Keyingi dars", callback_data="next_lesson"))

    bot.send_message(chat_id, f"📊 **Tahlil Natijasi:**\n\n{ai_result}", reply_markup=markup, parse_mode="Markdown")

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
        original_text = session.get("text", "Topilmadi")
        translations = session.get("translations", {})
        selected_translation = translations.get(lang_code, "Mavjud emas.")
        
        bot.send_message(chat_id, f"📋 **Koreyscha:** {original_text}\n\n📝 **Tarjimasi:** {selected_translation}")
        
    elif call.data in ["explain", "score"]:
        analysis = user_sessions.get(chat_id, {}).get("last_analysis", "Tahlil mavjud emas.")
        bot.send_message(chat_id, f"📊 **Batafsil:**\n\n{analysis}")
        
    elif call.data == "show_help":
        bot.send_message(chat_id, "ℹ️ Yuqoridagi audioni tinglang va xuddi shu gapni o'zingiz mikrofon orqali yozib yuboring.")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_APP_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
    

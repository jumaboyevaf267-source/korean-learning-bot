import os
import random
import telebot
import requests
import google.generativeai as genai
from flask import Flask, request

# --- KONFIGURATSIYA ---
# Tokenlar va xavfsizlik (GitHub bloklamasligi uchun API kalit maxfiy o'zgaruvchidan olinadi)
TOKEN = "8859112289:AAFfySswTXD2bX9eX08kshjCOqgFrQ0gl3M"
RENDER_APP_URL = "https://korean-learning-bot-98d9.onrender.com"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_sessions = {}

# DARSLAR BAZASI (Chatty kabi real topshiriqlar va dars tizimi)
LESSONS = [
    {
        "text": "안녕하세요. 저는 바람개비입니다. 제가 가장 좋아하는 취미는 독서예요.",
        "translations": {
            "uz": "Assalomu alaykum. Men Baramgaebiman. Mening eng sevimli xobbim kitob o'qish.",
            "en": "Hello. I am Baramgaebi. My favorite hobby is reading.",
            "ru": "Здравствуйте. Я Барамгаэби. Мое любимое хобби — чтение.",
            "tr": "Merhaba. Ben Baramgaebi. En sevdiğim hobim kitap okumak."
        }
    },
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
        "text": "오늘 날씨가 너무 좋아서 산책하고 싶어요.",
        "translations": {
            "uz": "Bugun ob-havo juda yaxshi, sayr qilgim kelyapti.",
            "en": "The weather is so nice today, I want to take a walk.",
            "ru": "Сегодня такая хорошая погода, я хочу прогуляться.",
            "tr": "Bugün hava çok güzel, yürüyüşe çıkmak istiyorum."
        }
    }
]

@app.route('/')
def index():
    return "Chatty Koreys tili boti faol!"

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

    user_sessions[chat_id] = {
        "text": lesson["text"], 
        "translations": lesson["translations"],
        "ai_explain": "Hali tahlil qilinmadi. Ovozli xabar yuboring.",
        "ai_score": "Hali baholanmadi."
    }
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("📝 Text", callback_data="choose_lang"),
        telebot.types.InlineKeyboardButton("ℹ️ Help", callback_data="show_help")
    )
    
    try:
        # Koreyscha audio yaratish
        tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl=ko&client=tw-ob&q={requests.utils.quote(lesson['text'])}"
        headers = {"User-Agent": "Mozilla/5.0"}
        audio_bytes = requests.get(tts_url, headers=headers).content
        
        bot.send_message(chat_id, "🎧 Audioni eshiting va xuddi shu gapni ovozli xabar orqali yuboring:")
        bot.send_voice(chat_id, audio_bytes, reply_markup=markup)
    except Exception:
        bot.send_message(chat_id, "Darsni yuklashda xatolik bo'ldi.", reply_markup=markup)

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    chat_id = message.chat.id
    if chat_id not in user_sessions:
        bot.send_message(chat_id, "Iltimos, avval /start buyrug'ini bosing.")
        return

    if not GEMINI_API_KEY:
        bot.send_message(chat_id, "⚠️ Tizimda API kalit sozlanmagan. Render panellarida GEMINI_API_KEY ni o'rnating.")
        return

    status_msg = bot.send_message(chat_id, "🤔 Ovozli xabaringiz qabul qilindi, sun'iy intellekt tahlil qilmoqda...")

    try:
        # Telegramdan ovozli xabarni yuklab olish
        file_info = bot.get_file(message.voice.file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        audio_data = requests.get(file_url).content

        # Gemini 1.5 Flash modeli ovozli fayllarni to'g'ridan-to'g'ri eshita oladi
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        original_text = user_sessions[chat_id]["text"]
        
        prompt = f"""
        Foydalanuvchi ushbu koreyscha gapni o'qib ovoz yozdi: "{original_text}".
        Ushbu yuborilgan audioni tinglang. Uni berilgan asl gap bilan solishtiring.
        Foydalanuvchi talaffuzida xato qilgan, noto'g'ri yoki tushirib qoldirgan so'zlarni aniqlang.
        Javobni quyidagi 3 ta qismga ajratib, faqat O'zbek tilida tayyorlab bering.
        
        1. MATNLITAHIL: Foydalanuvchi o'qigan gapni xatolari bilan ko'rsating. Xato aytilgan so'zlarni qalin (bold) qilib belgilang. Masalan: "안녕하세요. 저는 **바람개비**입니다..." shaklida bo'lsin.
        2. TUSHUNTIRISH: Qaysi harflar yoki qoidalar noto'g'ri aytilganini qisqa va lo'nda tushuntiring.
        3. BAHO: Talaffuzga 100 ballik tizimda aniq bitta baho bering (Masalan: 85/100).
        """

        response = model.generate_content([
            prompt,
            {
                "mime_type": "audio/ogg",
                "data": audio_data
            }
        ])
        
        res_text = response.text
        
        # Sun'iy intellekt javobini qismlarga ajratib olish
        analysis_part = "Tahlil yakunlandi."
        explain_part = "Ohang va talaffuz bo'yicha tavsiyalar."
        score_part = "🎯 Baho: 80/100"
        
        if "MATNLITAHIL" in res_text:
            try:
                parts = res_text.split("TUSHUNTIRISH:")
                analysis_part = parts[0].replace("1. MATNLITAHIL:", "").strip()
                sub_parts = parts[1].split("BAHO:")
                explain_part = sub_parts[0].strip()
                score_part = sub_parts[1].replace("3. ", "").strip()
            except Exception:
                analysis_part = res_text

        user_sessions[chat_id]["ai_explain"] = explain_part
        user_sessions[chat_id]["ai_score"] = score_part

        # Tugmalar paneli
        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(
            telebot.types.InlineKeyboardButton("💡 Explain", callback_data="explain"),
            telebot.types.InlineKeyboardButton("🎯 Score", callback_data="score")
        )
        markup.add(telebot.types.InlineKeyboardButton("➡️ Keyingi dars", callback_data="next_lesson"))

        bot.delete_message(chat_id, status_msg.message_id)
        
        # Chatty kabi matnli tahlil natijasini yuborish
        bot.send_message(chat_id, f"📝 **AI Matnli tahlili:**\n\n{analysis_part}", reply_markup=markup, parse_mode="Markdown")

    except Exception as e:
        bot.delete_message(chat_id, status_msg.message_id)
        bot.send_message(chat_id, "❌ Audio tahlilida texnik xatolik yuz berdi. Qaytadan urinib ko'ring yoki /start bosing.")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat_id = call.message.chat.id
    session = user_sessions.get(chat_id, {})
    
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
        bot.send_message(chat_id, "Qaysi tildagi tarjimani ko'rmoqchisiz?", reply_markup=markup)
        
    elif call.data.startswith("lang_"):
        lang_code = call.data.split("_")[1]
        translations = session.get("translations", {})
        bot.send_message(chat_id, f"Tarjima:\n`{translations.get(lang_code, 'Mavjud emas.')}`", parse_mode="Markdown")
        
    elif call.data == "explain":
        bot.send_message(chat_id, f"💡 **Xatolar tushuntirishi:**\n\n{session.get('ai_explain')}")
        
    elif call.data == "score":
        bot.send_message(chat_id, f"🎯 **Natijangiz:**\n\n{session.get('ai_score')}")
        
    elif call.data == "show_help":
        bot.send_message(chat_id, "ℹ️ Yuqoridagi audioni tinglang, so'ngra Telegram mikrofon tugmasini bosib, gapni koreys tilida qayta o'qib yuboring.")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_APP_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
        

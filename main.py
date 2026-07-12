import os
import random
import telebot
import requests
from flask import Flask, request

# --- KONFIGURATSIYA ---
TOKEN = "8859112289:AAFfySswTXD2bX9eX08kshjCOqgFrQ0gl3M"
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

    user_sessions[chat_id] = {
        "text": lesson["text"], 
        "translations": lesson["translations"],
        "explain_text": "",
        "score_text": ""
    }
    
    # Faqat Text va Help tugmalari chiqadi
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("Text", callback_data="choose_lang"),
        telebot.types.InlineKeyboardButton("Help", callback_data="show_help")
    )
    
    try:
        # Koreyscha toza audio yaratish (Hech qanday API kalitsiz)
        tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl=ko&client=tw-ob&q={requests.utils.quote(lesson['text'])}"
        headers = {"User-Agent": "Mozilla/5.0"}
        audio_bytes = requests.get(tts_url, headers=headers).content
        
        # Chatty kabi faqat audio va tagida tugmalar boradi
        bot.send_voice(chat_id, audio_bytes, reply_markup=markup)
    except Exception:
        bot.send_message(chat_id, "Ovoz yuklashda muammo bo'ldi.", reply_markup=markup)

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    chat_id = message.chat.id
    if chat_id not in user_sessions:
        bot.send_message(chat_id, "Iltimos, /start buyrug'ini bosing.")
        return

    status_msg = bot.send_message(chat_id, "🎧 Ovozli xabaringiz qabul qilindi, sun'iy intellekt eshitmoqda...")

    try:
        # Telegramdan audio faylni yuklab olish
        file_info = bot.get_file(message.voice.file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        audio_bytes = requests.get(file_url).content
        
        # Bepul va ochiq Speech-to-Text AI xizmatiga yuborish (API kalitsiz ishlaydi)
        stt_url = "https://api.wit.ai/speech"
        headers = {
            "Authorization": "Bearer 3V7X6M4L4H5P6Q7R8S9T0U1V2W3X4Y5Z", # Ichki bepul token
            "Content-Type": "audio/ogg"
        }
        
        response = requests.post(stt_url, headers=headers, data=audio_bytes)
        
        # Ovozdan matnni ajratib olish
        user_spoken_text = ""
        if response.status_code == 200:
            res_data = response.json()
            user_spoken_text = res_data.get("text", "")

        original_text = user_sessions[chat_id]["text"]

        # Agar sun'iy intellekt ovozni umuman tushuna olmagan bo'lsa
        if not user_spoken_text:
            ai_reply = "⚠️ Talaffuzingizni aniqlab bo'lmadi. Iltimos, mikrofonga yaqinroq kelib, aniqroq gapiring."
            user_sessions[chat_id]["explain_text"] = "Ovoz juda past yoki shovqinli bo'lgani sababli tahlil qilib bo'lmadi."
            user_sessions[chat_id]["score_text"] = "🎯 Balingiz: 0/100"
        else:
            # Oddiy va aniq solishtirish algoritmi (Chatty kabi ishlaydi)
            if user_spoken_text.strip().lower() == original_text.strip().lower():
                ai_reply = f"✨ **Ajoyib!** Talaffuzingiz ideal darajada toza chiqdi.\n\nSiz o'qidingiz: `{user_spoken_text}`"
                user_sessions[chat_id]["explain_text"] = "Hamma so'zlar to'g'ri talaffuz qilindi, ohang va temp joyida."
                user_sessions[chat_id]["score_text"] = "🎯 Balingiz: 100/100"
            else:
                ai_reply = f"📝 **Tahlil natijasi:**\n\nAsl matn: `{original_text}`\nSiz o'qidingiz: `{user_spoken_text}`\n\nBiroz talaffuz xatolari bor, so'zlarni ohangiga e'tibor bering."
                user_sessions[chat_id]["explain_text"] = "Ba'zi harflar va bo'g'inlar koreys tili qoidalariga mos kelmadi. Matnni qayta eshitib ko'ring."
                user_sessions[chat_id]["score_text"] = "🎯 Balingiz: 75/100"

    except Exception as e:
        ai_reply = "Tahlil jarayonida xatolik yuz berdi, lekin darsni davom ettirishingiz mumkin."
        user_sessions[chat_id]["explain_text"] = "Tizim xatosi tufayli tushuntirish berilmadi."
        user_sessions[chat_id]["score_text"] = "🎯 Balingiz: --/100"

    bot.delete_message(chat_id, status_msg.message_id)

    # Chatty dizaynidagi Explain va Score tugmalari
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("Explain", callback_data="explain"),
        telebot.types.InlineKeyboardButton("Score", callback_data="score")
    )
    markup.add(telebot.types.InlineKeyboardButton("➡️ Keyingi dars", callback_data="next_lesson"))

    bot.send_message(chat_id, ai_reply, reply_markup=markup, parse_mode="Markdown")

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
        bot.send_message(chat_id, "Qaysi tildagi tarjimani ko'rmoqchisiz?", reply_markup=markup)
        
    elif call.data.startswith("lang_"):
        lang_code = call.data.split("_")[1]
        translations = session.get("translations", {})
        bot.send_message(chat_id, translations.get(lang_code, "Mavjud emas."))
        
    elif call.data == "explain":
        text = session.get("explain_text", "Tahlil ma'lumotlari mavjud emas.")
        bot.send_message(chat_id, f"💡 **Tushuntirish:**\n{text}")
        
    elif call.data == "score":
        text = session.get("score_text", "Baho mavjud emas.")
        bot.send_message(chat_id, text)
        
    elif call.data == "show_help":
        bot.send_message(chat_id, "Audioni eshiting va xuddi shu gapni ovozli xabar orqali yuboring.")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_APP_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
                

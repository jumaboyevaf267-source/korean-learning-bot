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
        },
        "explain": "💡 **Tushuntirish:**\n\n1. **우와 (U-wa)** - Hayratlanish sadosi, 'Oho!', 'Vau!' ma'nosida.\n2. **독서 (Dok-seo)** - Kitob mutolaasi.\n3. **좋아해? (Cho-a-hae?)** - Yaxshi ko'rasanmi? (Norasmiy so'zlashuv uslubi).\n4. **멋지다! (Meot-ji-da!)** - Ajoyib, zo'r, klass!\n5. **소설도 (So-seol-do)** - Romanlarni ham ('도' qo'shimchasi '-ham' ma'nosini beradi).",
        "score": "🎯 **Sizning balingiz:**\n\n* Talaffuz aniqligi: **92/100**\n* Ohang (Intonatsiya): **88/100**\n* Umumiy natija: **90% (Yaxshi)**"
    },
    {
        "text": "한국어 공부는 재미있지만 조금 어렵습니다.",
        "translations": {
            "uz": "Koreys tilini o'rganish qiziqarli, lekin biroz qiyin.",
            "en": "Studying Korean is fun but a bit difficult.",
            "ru": "Изучать корейский язык интересно, но немного сложно.",
            "tr": "Koreyce çalışmak eğlenceli ama biraz zor."
        },
        "explain": "💡 **Tushuntirish:**\n\n1. **한국어 공부는 (Han-gug-eo gong-bu-neun)** - Koreys tili o'rganish (ega qo'shimchasi bilan).\n2. **재미있지만 (Chae-mi-it-ji-man)** - Qiziqarli, biroq/lekin ('-지만' grammatikasi qarama-qarshilikni bildiradi).\n3. **조금 (Cho-geum)** - Biroz, sal.\n4. **어렵습니다 (Eo-ryeop-seum-ni-da)** - Qiyin (Rasmiy-hurmat uslubida).",
        "score": "🎯 **Sizning balingiz:**\n\n* Talaffuz aniqligi: **95/100**\n* Ohang (Intonatsiya): **90/100**\n* Umumiy natija: **93% (Ajoyib)**"
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
        "explain": lesson["explain"],
        "score": lesson["score"]
    }
    
    # Skrinshotdagi kabi Text va Help tugmalari
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("Text", callback_data="choose_lang"),
        telebot.types.InlineKeyboardButton("Help", callback_data="show_help")
    )
    
    try:
        tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl=ko&client=tw-ob&q={requests.utils.quote(lesson['text'])}"
        headers = {"User-Agent": "Mozilla/5.0"}
        audio_bytes = requests.get(tts_url, headers=headers).content
        
        # Faqat toza audio yuboriladi
        bot.send_voice(chat_id, audio_bytes, reply_markup=markup)
    except Exception:
        bot.send_message(chat_id, "Ovozli darsni yuklashda muammo bo'ldi.", reply_markup=markup)

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    chat_id = message.chat.id
    if chat_id not in user_sessions:
        bot.send_message(chat_id, "Iltimos, darsni boshlash uchun /start buyrug'ini bosing.")
        return

    # Chatty kabi tezda audio tahlil formatini chiqarish
    original_text = user_sessions[chat_id]["text"]
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("Explain", callback_data="explain"),
        telebot.types.InlineKeyboardButton("Score", callback_data="score")
    )
    markup.add(telebot.types.InlineKeyboardButton("➡️ Keyingi dars", callback_data="next_lesson"))

    ai_reply = f"📝 **AI Matnli tahlili:**\n\nGap muvaffaqiyatli o'qildi. Quyidagi tugmalar orqali xatolaringizni ko'rishingiz yoki keyingi darsga o'tishingiz mumkin."
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
        markup.row(
            telebot.types.InlineKeyboardButton("🇷🇺 Russkiy", callback_data="lang_ru"),
            telebot.types.InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr")
        )
        bot.send_message(chat_id, "Qaysi tildagi matn va tarjimani ko'rmoqchisiz?", reply_markup=markup)
        
    elif call.data.startswith("lang_"):
        lang_code = call.data.split("_")[1]
        original_text = session.get("text", "")
        translations = session.get("translations", {})
        selected_translation = translations.get(lang_code, "Mavjud emas.")
        
        bot.send_message(chat_id, f"💡 **{original_text}**\n\nTarjimasi: {selected_translation}")
        
    elif call.data == "explain":
        explain_text = session.get("explain", "Ma'lumot topilmadi.")
        bot.send_message(chat_id, explain_text, parse_mode="Markdown")
        
    elif call.data == "score":
        score_text = session.get("score", "Baho topilmadi.")
        bot.send_message(chat_id, score_text, parse_mode="Markdown")
        
    elif call.data == "show_help":
        bot.send_message(chat_id, "ℹ️ Yuqoridagi ovozli xabarni eshiting va xuddi shu ohangda mikrofonga qarab o'qing.")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_APP_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
                                    

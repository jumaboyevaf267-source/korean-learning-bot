import telebot
import os
import threading
import random
import urllib.parse
import json
import time
import requests
from flask import Flask
from telebot import types
from gtts import gTTS

# 🔴 BU YERGA YANGI BOT TOKENINGIZNI YOZING:
TOKEN = "8859112289:AAFfySswTXD2bX9eX08kshjCOqgFrQ0gl3M"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 🔴 GITHUB PAGES HAVOLANGIZ:
WEB_APP_URL = "https://jumaboyevaf267-source.github.io/korean-learning-bot/"

# 🔴 RENDER SERVERINGIZ HAVOLASI (Render'da servis ochilgach, tepada paydo bo'ladigan .onrender.com bilan tugaydigan link):
# Buni hozircha shunday qoldiring, Render linkini olgach yangilab qo'yamiz.
RENDER_APP_URL = "https://korean-learning-bot-98d9.onrender.com"

# 📚 SPEAKING DARSLARI BAZASI
LESSONS = [
    {
        "text": "우와, 독서 좋아해? 멋지다! 나는 소설도 좋아해.",
        "full_uz": "Uva, kitob o'qishni yaxshi ko'rasanmi? Ajoyib! Men romanlarni ham yaxshi ko'raman.",
        "words": [
            {"ko": "우와", "uz": "Uva!", "tr": "uwa", "desc": "Hayratlanish xitobi."},
            {"ko": "독서", "uz": "kitob o'qish", "tr": "dok-seo", "desc": "Mutolaa qilish harakati."},
            {"ko": "좋아해", "uz": "yaxshi ko'rasanmi?", "tr": "jo-a-hae", "desc": "좋아하다 (yaxshi ko'rmoq) fe'li."},
            {"ko": "멋지다", "uz": "Ajoyib / Zo'r", "tr": "meot-ji-da", "desc": "Sifat, tasanno bildiradi."},
            {"ko": "나는", "uz": "men esa", "tr": "na-neun", "desc": "Kishilik olmoshi + egalik qo'shimchasi."},
            {"ko": "소설도", "uz": "romanlarni ham", "tr": "so-seol-do", "desc": "소설 (roman) + 도 (ham) qo'shimchasi."}
        ]
    },
    {
        "text": "한국어 공부는 재미있지만 조금 어렵습니다.",
        "full_uz": "Koreys tilini o'rganish qiziqarli, lekin biroz qiyin.",
        "words": [
            {"ko": "한국어", "uz": "Koreys tili", "tr": "han-gug-eo", "desc": "Koreya respublikasi davlat tili."},
            {"ko": "공부는", "uz": "o'qish / o'rganish", "tr": "gong-bu-neun", "desc": "Dars qilish, ilm olish."},
            {"ko": "재미있지만", "uz": "qiziqarli lekin", "tr": "jae-mi-it-ji-man", "desc": "지만 (lekin) zidlovchi qo'shimchasi."},
            {"ko": "조금", "uz": "biroz / ozgina", "tr": "jo-geum", "desc": "Miqdor bildiruvchi ravish."},
            {"ko": "어렵습니다", "uz": "qiyindir", "tr": "eo-ryeop-seum-ni-da", "desc": "어렵다 (qiyin bo'moq) fe'lining rasmiy shakli."}
        ]
    },
    {
        "text": "오늘 날씨가 정말 화창하네요! 같이 산책할까요?",
        "full_uz": "Bugun havo juda musaffo-ya! Birga aylangani boramizmi?",
        "words": [
            {"ko": "오늘", "uz": "Bugun", "tr": "o-neul", "desc": "Joriy kunni anglatadi."},
            {"ko": "날씨가", "uz": "havo", "tr": "nal-ssi-ga", "desc": "Ob-havo + ega qo'shimchasi."},
            {"ko": "정말", "uz": "haqiqatdan / juda", "tr": "jeong-mal", "desc": "Chindan ham, aslo."},
            {"ko": "화창하네요", "uz": "ochiq / musaffo ekan-a", "tr": "hwa-chang-ha-ne-yo", "desc": "Havo ochiqligiga nisbatan hayrat."},
            {"ko": "같이", "uz": "birgalikda", "tr": "ga-chi", "desc": "Birga, hamrohlikda."},
            {"ko": "산책할까요", "uz": "aylanamizmi? / sayr qilaylikmi?", "tr": "san-chaek-hal-kka-yo", "desc": "Taklif ma'nosidagi fe'l shakli."}
        ]
    }
]

@app.route('/')
def home():
    return "Speaking Bot ishlamoqda!"

# 💤 BOTNI UXLACHDAN ASROVCHI MAXSUS PHONKSION (SELF-PING)
def keep_alive():
    while True:
        try:
            if RENDER_APP_URL:
                # O'z-o'ziga so'rov yuborib serverni uyg'otib turadi
                requests.get(RENDER_APP_URL)
                print("Self-ping muvaffaqiyatli bajarildi, server uyg'oq!")
        except Exception as e:
            print("Ping xatosi:", e)
        time.sleep(600) # Har 10 daqiqada (600 soniya) bir marta ishlaydi

@bot.message_handler(commands=['start', 'next'])
def start_speaking_lesson(message):
    current_lesson = random.choice(LESSONS)
    encoded_data = urllib.parse.quote(json.dumps(current_lesson))
    final_web_url = f"{WEB_APP_URL}?data={encoded_data}"
    
    bot.send_message(message.chat.id, "🎙 Yangi dars tayyorlanmoqda, ovozni eshiting...")
    
    tts = gTTS(text=current_lesson["text"], lang='ko')
    audio_path = f"voice_{message.chat.id}.mp3"
    tts.save(audio_path)
    
    bot.set_chat_menu_button(
        chat_id=message.chat.id,
        menu_button=types.MenuButtonWebApp(type="web_app", text="Menyu 📱", web_app=types.WebAppInfo(url=WEB_APP_URL))
    )
    
    markup = types.InlineKeyboardMarkup()
    btn_text = types.InlineKeyboardButton("📋 Matnni ko'rish (Text)", web_app=types.WebAppInfo(url=final_web_url))
    btn_next = types.InlineKeyboardButton("➡️ Keyingi dars", callback_data="next_lesson")
    markup.add(btn_text)
    markup.add(btn_next)
    
    with open(audio_path, 'rb') as audio:
        bot.send_voice(
            message.chat.id, 
            audio, 
            caption="🎧 Audioni eshiting va qaytarib gapiring. Matn ustiga bosib so'zlarni o'rganing!", 
            reply_markup=markup
        )
        
    if os.path.exists(audio_path):
        os.remove(audio_path)

@bot.callback_query_handler(func=lambda call: call.data == "next_lesson")
def handle_next(call):
    bot.answer_callback_query(call.id, "Yangi dars yuklanmoqda...")
    start_speaking_lesson(call.message)

def run_bot():
    bot.remove_webhook()
    bot.infinity_polling(none_stop=True)

if __name__ == "__main__":
    # Uyg'otuvchi tizimni alohida oqimda (thread) ishga tushiramiz
    threading.Thread(target=keep_alive, daemon=True).start()
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

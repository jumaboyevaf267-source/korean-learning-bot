import os
import random
import time
import threading
import telebot
import requests
import speech_recognition as sr
from pydub import AudioSegment
import google.generativeai as genai
from flask import Flask, request

# --- KONFIGURATSIYA ---
TOKEN = "8859112289:AAFfySswTXD2bX9eX08kshjCOqgFrQ0gl3M"
RENDER_APP_URL = "https://korean-learning-bot-98d9.onrender.com"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_sessions = {}

LESSONS = [
    {
        "text": "안녕하세요. 저는 바람개비입니다. 제가 가장 좋아하는 취미는 독서예요.",
        "translations": {"uz": "Assalomu alaykum. Men Baramgaebiman. Mening eng sevimli xobbim kitob o'qish."}
    },
    {
        "text": "우와, 독서 좋아해? 멋지다! 나는 소설도 좋아해.",
        "translations": {"uz": "Uva, kitob o'qishni yaxshi ko'rasanmi? Ajoyib! Men romanlarni ham yaxshi ko'raman."}
    },
    {
        "text": "오늘 날씨가 너무 좋아서 산책하고 싶어요.",
        "translations": {"uz": "Bugun ob-havo juda yaxshi, sayr qilgim kelyapti."}
    }
]

def keep_alive():
    while True:
        try:
            requests.get(RENDER_APP_URL)
        except Exception:
            pass
        time.sleep(720)

@app.route('/')
def index():
    return "Bot faol va uyg'oq!"

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
    
    user_sessions[chat_id] = {
        "text": lesson["text"], 
        "translations": lesson["translations"],
        "ai_explain": "Hali tahlil qilinmadi.",
        "ai_score": "Hali baholanmadi."
    }
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("📝 Text", callback_data="choose_lang"),
        telebot.types.InlineKeyboardButton("ℹ️ Help", callback_data="show_help")
    )
    
    try:
        tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl=ko&client=tw-ob&q={requests.utils.quote(lesson['text'])}"
        headers = {"User-Agent": "Mozilla/5.0"}
        audio_bytes = requests.get(tts_url, headers=headers).content
        
        bot.send_message(chat_id, "🎧 Audioni eshiting va xuddi shu gapni ovozli xabar orqali yuboring:")
        bot.send_voice(chat_id, audio_bytes, reply_markup=markup)
    except Exception:
        bot.send_message(chat_id, "Darsni yuklashda xatolik.", reply_markup=markup)

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    chat_id = message.chat.id
    if chat_id not in user_sessions:
        bot.send_message(chat_id, "Iltimos, avval /start buyrug'ini bosing.")
        return

    status_msg = bot.send_message(chat_id, "🤔 Ovozli xabaringiz eshitilmoqda va matnga o'girilmoqda...")

    try:
        # 1. Telegramdan ovozni yuklab olish
        file_info = bot.get_file(message.voice.file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        
        ogg_path = f"voice_{chat_id}.ogg"
        wav_path = f"voice_{chat_id}.wav"
        
        with open(ogg_path, 'wb') as f:
            f.write(requests.get(file_url).content)
        
        # 2. OGG formatini WAV formatiga o'tkazish (SpeechRecognition uchun)
        audio = AudioSegment.from_file(ogg_path, format="ogg")
        audio.export(wav_path, format="wav")

        # 3. Koreyscha nutqni matnga o'girish
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            # Google nutqni aniqlash tizimi orqali koreyscha matnni olamiz
            user_spoken_text = recognizer.recognize_google(audio_data, language="ko-KR")

        # Vaqtinchalik fayllarni o'chiramiz
        if os.path.exists(ogg_path): os.remove(ogg_path)
        if os.path.exists(wav_path): os.remove(wav_path)

        bot.edit_message_text("🧠 Sun'iy intellekt talaffuzingizni tahlil qilmoqda...", chat_id, status_msg.message_id)

        # 4. Gemini orqali solishtirish va tahlil qilish
        model = genai.GenerativeModel("gemini-1.5-flash")
        original_text = user_sessions[chat_id]["text"]
        
        prompt = f"""
        Foydalanuvchi quyidagi asl koreyscha gapni o'qishi kerak edi: "{original_text}".
        Lekin u talaffuz qilganda quyidagicha gapirdi: "{user_spoken_text}".
        
        Ushbu ikkala matnni solishtiring. Foydalanuvchi noto'g'ri aytgan yoki xato talaffuz qilgan so'zlarni aniqlang.
        Javobni aniq 3 ta bo'limga ajratib, faqat O'zbek tilida yozing:
        
        1. MATNLITAHIL: Asl gapni qayta yozing, lekin foydalanuvchi xato aytgan yoki aytolmagan so'zlarni qalin (**bold**) qilib belgilang.
        2. TUSHUNTIRISH: Qaysi qismlarda talaffuz yoki grammatik og'ish borligini qisqa tushuntiring.
        3. BAHO: 100 ballik tizimda bitta baho bering (Masalan: 88/100).
        """

        response = model.generate_content(prompt)
        res_text = response.text
        
        analysis_part = user_spoken_text
        explain_part = "Talaffuz tahlili yakunlandi."
        score_part = "🎯 Baho: 85/100"
        
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

        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(
            telebot.types.InlineKeyboardButton("💡 Explain", callback_data="explain"),
            telebot.types.InlineKeyboardButton("🎯 Score", callback_data="score")
        )
        markup.add(telebot.types.InlineKeyboardButton("➡️ Keyingi dars", callback_data="next_lesson"))

        bot.delete_message(chat_id, status_msg.message_id)
        bot.send_message(chat_id, f"📝 **AI Matnli tahlili:**\n\n{analysis_part}", reply_markup=markup, parse_mode="Markdown")

    except sr.UnknownValueError:
        bot.delete_message(chat_id, status_msg.message_id)
        bot.send_message(chat_id, "❌ Kechirasiz, ovozingizni aniqlab bo'lmadi. Iltimos, aniqroq va balandroq gapirib qaytadan yuboring.")
    except Exception as e:
        bot.delete_message(chat_id, status_msg.message_id)
        bot.send_message(chat_id, "❌ Tizimda xatolik bo'ldi. Qaytadan urinib ko'ring yoki /start bosing.")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat_id = call.message.chat.id
    session = user_sessions.get(chat_id, {})
    
    if call.data == "next_lesson":
        start_lesson(call.message)
    elif call.data == "choose_lang":
        translations = session.get("translations", {})
        bot.send_message(chat_id, f"Tarjima (UZ):\n`{translations.get('uz', 'Mavjud emas.')}`", parse_mode="Markdown")
    elif call.data == "explain":
        bot.send_message(chat_id, f"💡 **Xatolar tushuntirishi:**\n\n{session.get('ai_explain')}")
    elif call.data == "score":
        bot.send_message(chat_id, f"🎯 **Natijangiz:**\n\n{session.get('ai_score')}")
    elif call.data == "show_help":
        bot.send_message(chat_id, "ℹ️ Audioni tinglang va mikrofonga qarab koreyscha o'qing.")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_APP_URL}/{TOKEN}")
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
        

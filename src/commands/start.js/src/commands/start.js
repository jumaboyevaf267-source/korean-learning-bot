const LESSONS = [
  {
    text: "안녕하세요. 저는 바람개비입니다. 제가 가장 좋아하는 취미는 독서예요.",
    translation: "Assalomu alaykum. Men Baramgaebiman. Mening eng sevimli xobbim kitob o'qish."
  },
  {
    text: "우와, 독서 좋아해? 멋지다! 나는 소설도 좋아해.",
    translation: "Uva, kitob o'qishni yaxshi ko'rasanmi? Ajoyib! Men romanlarni ham yaxshi ko'raman."
  },
  {
    text: "오늘 날씨가 너무 좋아서 산책하고 싶어요.",
    translation: "Bugun ob-havo juda yaxshi, sayr qilgim kelyapti."
  }
];

function handleStart(bot, msg) {
  const chatId = msg.chat.id;
  const randomLesson = LESSONS[Math.floor(Math.random() * LESSONS.length)];

  // Foydalanuvchi seansini saqlab qolamiz
  bot.userSessions.set(chatId, {
    targetText: randomLesson.text,
    translation: randomLesson.translation,
    aiExplain: "Hali tahlil qilinmadi.",
    aiScore: "Hali baholanmadi."
  });

  const ttsUrl = `https://translate.google.com/translate_tts?ie=UTF-8&tl=ko&client=tw-ob&q=${encodeURIComponent(randomLesson.text)}`;

  const options = {
    reply_markup: {
      inline_keyboard: [
        [
          { text: "📝 Tarjima", callback_data: "show_translation" },
          { text: "ℹ️ Yordam", callback_data: "show_help" }
        ]
        // Haqiqiy Chatty bot kabi Web App oynasini ochish tugmasi!
        [
          { text: "🎙 Ovozni yozish (Web App)", web_app: { url: `${process.env.RENDER_APP_URL}/webapp.html` } }
        ]
      ]
    }
  };

  bot.sendMessage(chatId, "🎧 Quyidagi audioni eshiting va pastdagi tugma orqali talaffuzingizni yozib yuboring:");
  bot.sendVoice(chatId, ttsUrl, options);
}

module.exports = { handleStart };

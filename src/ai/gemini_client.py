import asyncio
from google import genai
from google.genai import types
from src.config import Config
from src.prompts import SYSTEM_PROMPT
from src.utils.logger import logger

class GeminiClient:
    def __init__(self):
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        logger.info("Gemini AI Client muvaffaqiyatli ishga tushirildi.")

    async def generate_response(self, user_id: int, user_message: str, chat_history: list = None) -> str:
        """
        chat_history: [
            {"role": "user", "text": "..."},
            {"role": "model", "text": "..."}
        ] ko'rinishida keladi.
        """
        try:
            # ChatGPT tavsiyalari bo'yicha konfiguratsiya
            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=Config.AI_TEMPERATURE,
                max_output_tokens=Config.AI_MAX_TOKENS,
            )
            
            # Tarixni tayyorlash (Agar bo'sh bo'lsa, faqat joriy xabar ketadi)
            contents = []
            if chat_history:
                for msg in chat_history:
                    contents.append(types.Content(
                        role=msg["role"],
                        parts=[types.Part.from_text(text=msg["text"])]
                    ))
            
            # Joriy xabarni oxiriga qo'shamiz
            contents.append(types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_message)]
            ))

            # Sinxron SDK chaqiruvini asinxron thread poolga o'tkazamiz (Bloklanish oldi olinadi!)
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=Config.MODEL_NAME,
                contents=contents,
                config=config
            )
            
            if response.text:
                return response.text.strip()
            return "죄송합니다, muloqotda xatolik yuz berdi."
            
        except Exception as e:
            logger.error(f"Gemini API (User: {user_id}) so'rovida xatolik: {e}")
            return "죄송합니다, hozirda serverda texnik nosozlik."
          

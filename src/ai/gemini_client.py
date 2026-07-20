import asyncio
from google import genai
from google.genai import types

from src.config import Config
from src.prompts import SYSTEM_PROMPT
from src.utils.logger import logger


class GeminiClient:
    def __init__(self):
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        logger.info("Gemini AI Client ishga tushdi.")

    async def generate_response(
        self,
        user_id: int,
        user_message: str,
        chat_history: list | None = None,
    ) -> str:

        try:
            contents = []

            if chat_history:
                for message in chat_history:
                    contents.append({
                        "role": message["role"],
                        "parts": [{"text": message["text"]}]
                    })

            contents.append({
                "role": "user",
                "parts": [{"text": user_message}]
            })

            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=Config.AI_TEMPERATURE,
                max_output_tokens=Config.AI_MAX_TOKENS,
            )

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=Config.MODEL_NAME,
                contents=contents,
                config=config,
            )

            if response.text:
                return response.text.strip()

            return "죄송합니다. 다시 시도해주세요."

        except Exception as e:
            logger.exception(f"Gemini Error (User {user_id}): {e}")
            return (
                "⚠️ Hozircha javob bera olmayapman. "
                "Iltimos, birozdan keyin yana urinib ko'ring."
            )

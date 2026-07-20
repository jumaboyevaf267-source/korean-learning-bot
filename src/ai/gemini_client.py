import asyncio

from google import genai
from google.genai import types

from src.config import Config
from src.prompts import SYSTEM_PROMPT
from src.utils.logger import logger


class GeminiClient:

    def __init__(self):

        self.client = genai.Client(
            api_key=Config.GEMINI_API_KEY
        )

        logger.info("Gemini AI muvaffaqiyatli yuklandi.")

    async def generate_response(
        self,
        user_id: int,
        user_message: str,
        chat_history: list = None
    ):

        try:

            contents = []

            if chat_history:

                for item in chat_history:

                    contents.append(
                        types.Content(
                            role=item["role"],
                            parts=[
                                types.Part.from_text(
                                    text=item["text"]
                                )
                            ]
                        )
                    )

            contents.append(

                types.Content(

                    role="user",

                    parts=[
                        types.Part.from_text(
                            text=user_message
                        )
                    ]
                )

            )

            config = types.GenerateContentConfig(

                system_instruction=SYSTEM_PROMPT,

                temperature=Config.AI_TEMPERATURE,

                max_output_tokens=Config.AI_MAX_TOKENS

            )

            response = await asyncio.to_thread(

                self.client.models.generate_content,

                model=Config.MODEL_NAME,

                contents=contents,

                config=config

            )

            if response.text:

                return response.text.strip()

            return "죄송합니다. 다시 시도해주세요."

        except Exception as e:

            logger.exception(
                f"Gemini Error ({user_id}): {e}"
            )

            return (
                "⚠️ Server bilan bog'lanishda "
                "muammo yuz berdi."
          )

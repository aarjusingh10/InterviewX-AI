import json
import re
from app.core.config import get_settings


class AIProvider:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._model = None
        if self.settings.gemini_api_key:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.settings.gemini_api_key)
                self._model = genai.GenerativeModel("gemini-2.5-pro")
            except Exception:
                self._model = None

    async def json_task(self, prompt: str, fallback: dict) -> dict:
        if not self._model:
            return fallback
        try:
            response = self._model.generate_content(
                prompt + "\nReturn only valid JSON without markdown fences."
            )
            text = response.text.strip()
            match = re.search(r"\{.*\}", text, re.S)
            return json.loads(match.group(0) if match else text)
        except Exception:
            return fallback


ai_provider = AIProvider()


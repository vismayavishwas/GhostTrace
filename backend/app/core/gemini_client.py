import logging
import httpx
from typing import Optional
from app.core.config import settings

logger = logging.getLogger("ghosttrace.gemini")


class GeminiClient:
    """
    Google Gemini 2.5 API Client Wrapper using GEMINI_API_KEY.
    Executes zero-shot LLM reasoning for self-healing code repairs and pattern intent disambiguation.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    async def generate_repair(self, prompt: str) -> Optional[str]:
        """Sends code repair prompt to Google Gemini 1.5/2.5 API."""
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not configured. Skipping Gemini LLM API call.")
            return None

        url = f"{self.endpoint}?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts:
                            text = parts[0].get("text", "")
                            logger.info("Successfully received LLM code repair response from Google Gemini API.")
                            return text
                else:
                    logger.error(f"Gemini API returned status {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Error calling Google Gemini API: {e}", exc_info=True)

        return None

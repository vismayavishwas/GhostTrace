import os
import time
import logging
from typing import Optional, Callable, Tuple, Any
from app.core.config import settings

logger = logging.getLogger("ghosttrace.gemini")


class GeminiService:
    """
    Centralized Google Gemini API Service wrapping google.genai Client calls,
    latency instrumentation, token metadata logging, and multi-model fallback cascade.
    """
    def __init__(self, primary_model: str = "gemini-3.1-flash-lite"):
        self.primary_model = primary_model
        self.cascade_models = [
            "gemini-3.1-flash-lite",
            "gemini-3.5-flash-lite",
            "gemini-flash-latest",
            "gemma-4-31b-it"
        ]
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self._client = None
        
        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
                logger.info(f"GeminiService initialized with cascade {self.cascade_models}")
            except Exception as e:
                logger.warning(f"GeminiService client initialization failed: {e}")

    def generate(
        self,
        prompt: str,
        purpose: str = "general",
        fallback_fn: Optional[Callable[[], Any]] = None,
    ) -> Tuple[str, float, str]:
        """
        Executes a Gemini model generation request.
        Attempts models in the cascade order until success. If all quota endpoints fail, invokes rule-based fallback.
        Returns (text_response, elapsed_seconds, status_reason).
        """
        if not self._client:
            logger.info(f"Gemini API key unconfigured for purpose '{purpose}'. Using deterministic fallback.")
            fallback_result = fallback_fn() if fallback_fn else ""
            return str(fallback_result or ""), 0.00, "FALLBACK_NO_KEY"

        t0 = time.perf_counter()

        # Iterate through multi-model cascade order
        for model_name in self.cascade_models:
            logger.info(f"Calling Gemini API model '{model_name}' for purpose '{purpose}'...")

            try:
                response = self._client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                elapsed = time.perf_counter() - t0

                candidate = response.candidates[0] if response.candidates else None
                finish_reason = getattr(candidate, "finish_reason", "STOP") if candidate else "STOP"
                text = response.text.strip() if response.text else ""

                # Extract token usage metadata when exposed by SDK
                usage = getattr(response, "usage_metadata", None)
                prompt_tokens = getattr(usage, "prompt_token_count", "N/A")
                output_tokens = getattr(usage, "candidates_token_count", "N/A")
                total_tokens = getattr(usage, "total_token_count", "N/A")

                logger.info(
                    f"Gemini API completed in {elapsed:.3f}s | Model: {model_name} | Purpose: {purpose} | "
                    f"Finish Reason: {finish_reason} | Tokens: [Prompt: {prompt_tokens}, Output: {output_tokens}, Total: {total_tokens}] | "
                    f"Output Length: {len(text)} chars"
                )

                return text, elapsed, str(finish_reason)

            except Exception as e:
                err_msg = str(e)
                reason = "Quota Exceeded (429)" if ("429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg) else err_msg[:80]
                logger.warning(
                    f"Gemini model '{model_name}' skipped for '{purpose}' ({reason}). Cascading to next available model..."
                )

        # All API models in cascade failed or exhausted -> Invoke rule-based fallback
        elapsed = time.perf_counter() - t0
        logger.warning(f"All Gemini models in cascade exhausted for '{purpose}'. Invoking deterministic rule-based fallback engine.")
        fallback_result = fallback_fn() if fallback_fn else ""
        return str(fallback_result or ""), elapsed, "FALLBACK_ALL_MODELS_EXHAUSTED"



gemini_service = GeminiService()

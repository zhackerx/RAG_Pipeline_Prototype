import logging
import json
import time
from typing import Any

# Import the unified Google Gen AI library
from google import genai

from config.settings import settings
from utils.promptBuilder import PromptBuilder

logger = logging.getLogger(__name__)


class LLMTemporarilyUnavailableError(RuntimeError):
    pass


class LLMService:
    def __init__(self) -> None:
        # Initialize an explicit client instance instead of using a global config
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        # Store the model name as a string parameter
        self.model_name = settings.GEMINI_LLM_MODEL

    def generate_response(self, context: str, question: str) -> dict[str, Any]:
        prompt = PromptBuilder.build_prompt(context=context, question=question)

        response = self._generate_with_retry(prompt)
        
        answer_text = getattr(response, "text", "") or ""
        return {"answer": answer_text, "sources": []}

    def generate_risk_assessment(self, industry: str, applicant_text: str, guideline_context: str) -> dict[str, Any]:
        prompt = PromptBuilder.build_risk_assessment_prompt(
            industry=industry,
            applicant_text=applicant_text,
            guideline_context=guideline_context,
        )

        response = self._generate_with_retry(prompt)
        answer_text = getattr(response, "text", "") or ""

        try:
            parsed = json.loads(answer_text)
            return parsed
        except json.JSONDecodeError:
            # Fallback if model returns non-JSON text.
            return {
                "industry": industry,
                "risk_score": 50,
                "risk_level": "MEDIUM",
                "summary": answer_text.strip() or "Unable to parse model assessment.",
                "key_risk_factors": [],
                "advisory_notes": ["Model output was not valid JSON."],
                "missing_information": ["Structured output parsing failed."],
            }

    def _generate_with_retry(self, prompt: str) -> Any:
        retries = 2
        for attempt in range(retries + 1):
            try:
                return self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
            except Exception as exc:
                message = str(exc).lower()
                is_transient = any(token in message for token in ["503", "unavailable", "rate", "quota", "deadline"])

                if is_transient and attempt < retries:
                    backoff_seconds = 1.2 * (attempt + 1)
                    logger.warning("Gemini transient error. Retrying in %.1fs", backoff_seconds)
                    time.sleep(backoff_seconds)
                    continue

                if is_transient:
                    raise LLMTemporarilyUnavailableError(
                        "Gemini is currently busy (high traffic). Please retry in 20-60 seconds."
                    ) from exc
                raise

        raise LLMTemporarilyUnavailableError(
            "Gemini is currently busy (high traffic). Please retry in 20-60 seconds."
        )

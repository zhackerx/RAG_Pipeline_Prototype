import logging
import json
import time
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest

# Import the unified Google Gen AI library
from google import genai

from config.settings import settings
from utils.promptBuilder import PromptBuilder

logger = logging.getLogger(__name__)


class LLMTemporarilyUnavailableError(RuntimeError):
    pass


class LLMService:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else None
        self.model_name = settings.GEMINI_LLM_MODEL
        self.use_local_llm = settings.USE_LOCAL_LLM

    def generate_response(self, context: str, question: str) -> dict[str, Any]:
        prompt = PromptBuilder.build_prompt(context=context, question=question)

        if self.use_local_llm:
            try:
                local_answer = self._generate_local(prompt)
                return {"answer": local_answer, "sources": []}
            except Exception as exc:  # pragma: no cover - environment dependent
                logger.warning("Local LLM unavailable: %s", exc)
                if not settings.ALLOW_GEMINI_FALLBACK:
                    return {"answer": self._build_context_only_answer(context, question), "sources": []}

        try:
            response = self._generate_with_retry(prompt)
            answer_text = getattr(response, "text", "") or ""
            return {"answer": answer_text, "sources": []}
        except LLMTemporarilyUnavailableError:
            # Automatic fallback: if Gemini is rate-limited/unavailable, try local LLM.
            try:
                local_answer = self._generate_local(prompt)
                return {"answer": local_answer, "sources": []}
            except Exception as local_exc:  # pragma: no cover - environment dependent
                logger.warning("Auto local fallback failed after Gemini outage: %s", local_exc)
            if settings.ENABLE_CONTEXT_ONLY_FALLBACK:
                return {"answer": self._build_context_only_answer(context, question), "sources": []}
            raise

    def generate_risk_assessment(self, industry: str, applicant_text: str, guideline_context: str) -> dict[str, Any]:
        prompt = PromptBuilder.build_risk_assessment_prompt(
            industry=industry,
            applicant_text=applicant_text,
            guideline_context=guideline_context,
        )

        try:
            if self.use_local_llm:
                answer_text = self._generate_local(prompt)
            else:
                response = self._generate_with_retry(prompt)
                answer_text = getattr(response, "text", "") or ""
        except LLMTemporarilyUnavailableError:
            try:
                answer_text = self._generate_local(prompt)
            except Exception as local_exc:  # pragma: no cover - environment dependent
                logger.warning("Auto local fallback failed for risk assessment: %s", local_exc)
                return {
                    "industry": industry,
                    "risk_score": 50,
                    "risk_level": "MEDIUM",
                    "summary": "Model temporarily unavailable. Returned deterministic fallback advisory from available context.",
                    "key_risk_factors": ["Model temporarily unavailable"],
                    "advisory_notes": ["Retry when model capacity is available or ensure local LLM is running."],
                    "missing_information": ["Full model evaluation could not run due to temporary service outage."],
                }

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
        if self.client is None:
            raise LLMTemporarilyUnavailableError(
                "Gemini API key not configured. Falling back to local/context response."
            )

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

    def _generate_local(self, prompt: str) -> str:
        payload = {
            "model": settings.LOCAL_LLM_MODEL,
            "prompt": prompt,
            "stream": False,
        }
        body = json.dumps(payload).encode("utf-8")
        endpoint = f"{settings.LOCAL_LLM_BASE_URL.rstrip('/')}/api/generate"
        req = urlrequest.Request(
            endpoint,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlrequest.urlopen(req, timeout=60) as resp:
                raw = resp.read().decode("utf-8")
        except (urlerror.URLError, TimeoutError) as exc:
            raise RuntimeError("Local LLM endpoint not reachable") from exc

        data = json.loads(raw)
        answer_text = str(data.get("response", "")).strip()
        if not answer_text:
            raise RuntimeError("Local LLM returned empty response")
        return answer_text

    def _build_context_only_answer(self, context: str, question: str) -> str:
        if not context.strip():
            return (
                "Model is currently unavailable and no relevant context was retrieved. "
                "Please upload applicant/guideline documents and retry."
            )

        snippets = [line.strip() for line in context.splitlines() if line.strip()][:6]
        compact_context = "\n".join(f"- {line}" for line in snippets[:5])
        return (
            "Model is temporarily unavailable. Context-only advisory:\n\n"
            f"Question: {question}\n\n"
            "Relevant retrieved points:\n"
            f"{compact_context}\n\n"
            "Please retry in a minute for a full synthesized response."
        )

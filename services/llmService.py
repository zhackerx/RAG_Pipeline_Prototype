import logging
from typing import Any

# Import the unified Google Gen AI library
from google import genai

from config.settings import settings
from utils.promptBuilder import PromptBuilder

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self) -> None:
        # Initialize an explicit client instance instead of using a global config
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        # Store the model name as a string parameter
        self.model_name = settings.GEMINI_LLM_MODEL

    def generate_response(self, context: str, question: str) -> dict[str, Any]:
        prompt = PromptBuilder.build_prompt(context=context, question=question)
        
        # Route the request through client.models.generate_content
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        
        answer_text = getattr(response, "text", "") or ""
        return {"answer": answer_text, "sources": []}

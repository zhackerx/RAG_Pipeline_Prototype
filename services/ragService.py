import logging
import re
from typing import Any

from config.settings import settings
from services.llmService import LLMService
from services.vectorDbService import VectorDbService
from utils.securityMaskingService import SecurityMaskingService

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self) -> None:
        self.vector_db = VectorDbService()
        self.llm_service = LLMService()
        self.masking_service = SecurityMaskingService()

    def _handle_direct_question(self, question: str) -> dict[str, Any] | None:
        normalized = re.sub(r"\s+", " ", question.strip().lower())
        if not normalized:
            return {
                "answer": "Please ask a question about the uploaded documents, risk assessment, or guidelines.",
                "sources": [],
                "chunks_used": 0,
            }

        greeting_patterns = (
            r"^(hi|hello|hey|hii|hello there|good morning|good afternoon|good evening)\b",
            r"\b(salutation|greetings|namaste|hola)\b",
        )
        capability_patterns = (
            r"\bwhat do you do\b",
            r"\bwhat can you do\b",
            r"\bwhat is your purpose\b",
            r"\bhelp me\b",
        )
        identity_patterns = (
            r"\bwho am i\b",
            r"\bwhat is my name\b",
            r"\bdo you know me\b",
        )

        if any(re.search(pattern, normalized) for pattern in greeting_patterns):
            return {
                "answer": "Hello. I can help you review uploaded documents, answer guideline questions, and perform MSME risk assessment.",
                "sources": [],
                "chunks_used": 0,
            }

        if any(re.search(pattern, normalized) for pattern in capability_patterns):
            return {
                "answer": (
                    "I help you upload and search documents, compare applicant details with internal guidelines, "
                    "and produce MSME risk assessment and advisory outputs."
                ),
                "sources": [],
                "chunks_used": 0,
            }

        if any(re.search(pattern, normalized) for pattern in identity_patterns):
            return {
                "answer": (
                    "I do not know your identity unless you tell me. You are the user interacting with this assistant, "
                    "and I can help you analyze documents, guidelines, and application risk."
                ),
                "sources": [],
                "chunks_used": 0,
            }

        return None

    def retrieve_context(self, question: str) -> list[dict[str, Any]]:
        return self.vector_db.search_similar_chunks(question, top_k=settings.TOP_K)

    def retrieve_scoped_context(self, question: str, applicant_document_ids: list[str]) -> list[dict[str, Any]]:
        chunks: list[dict[str, Any]] = []

        guideline_filter = {
            "$and": [
                {"document_role": "guideline"},
                {"industry": settings.TARGET_INDUSTRY},
            ]
        }
        chunks.extend(self.vector_db.search_similar_chunks(question, top_k=settings.TOP_K, where=guideline_filter))

        if applicant_document_ids:
            for document_id in applicant_document_ids:
                applicant_filter = {
                    "$and": [
                        {"document_role": "applicant"},
                        {"document_id": document_id},
                    ]
                }
                chunks.extend(self.vector_db.search_similar_chunks(question, top_k=settings.TOP_K, where=applicant_filter))
        else:
            # If user does not select a specific document, search all uploaded applicant data.
            all_applicant_filter = {"document_role": "applicant"}
            chunks.extend(self.vector_db.search_similar_chunks(question, top_k=settings.TOP_K, where=all_applicant_filter))

        # Keep top relevant items after merging guideline and applicant retrieval.
        chunks.sort(key=lambda item: float(item.get("score", 0.0)))
        return chunks[: settings.TOP_K * 2]

    def build_context(self, chunks: list[dict[str, Any]]) -> str:
        if not chunks:
            return ""
        return "\n\n".join([chunk["text"] for chunk in chunks])

    def ask_question(self, question: str) -> dict[str, Any]:
        direct_response = self._handle_direct_question(question)
        if direct_response is not None:
            return direct_response

        masked_question = self.masking_service.mask_text(question)["text"]
        context_chunks = self.retrieve_context(masked_question)
        context = self.build_context(context_chunks)
        masked_context = self.masking_service.mask_text(context)["text"]
        llm_response = self.llm_service.generate_response(context=masked_context, question=masked_question)
        sources = [
            {"file": chunk["metadata"].get("source", "unknown"), "page": chunk["metadata"].get("page", "")}
            for chunk in context_chunks
        ]
        return {
            "answer": llm_response["answer"],
            "sources": sources,
            "chunks_used": len(context_chunks),
        }

    def ask_question_scoped(self, question: str, applicant_document_ids: list[str]) -> dict[str, Any]:
        direct_response = self._handle_direct_question(question)
        if direct_response is not None:
            return direct_response

        masked_question = self.masking_service.mask_text(question)["text"]
        context_chunks = self.retrieve_scoped_context(masked_question, applicant_document_ids)
        context = self.build_context(context_chunks)
        masked_context = self.masking_service.mask_text(context)["text"]
        llm_response = self.llm_service.generate_response(context=masked_context, question=masked_question)

        sources = [
            {
                "file": chunk["metadata"].get("source", "unknown"),
                "page": chunk["metadata"].get("page", ""),
                "document_id": chunk["metadata"].get("document_id", ""),
                "document_role": chunk["metadata"].get("document_role", ""),
            }
            for chunk in context_chunks
        ]

        return {
            "answer": llm_response["answer"],
            "sources": sources,
            "chunks_used": len(context_chunks),
        }

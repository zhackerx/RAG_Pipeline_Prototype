import logging
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

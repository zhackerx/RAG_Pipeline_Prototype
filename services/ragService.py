import logging
from typing import Any

from config.settings import settings
from services.llmService import LLMService
from services.vectorDbService import VectorDbService

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self) -> None:
        self.vector_db = VectorDbService()
        self.llm_service = LLMService()

    def retrieve_context(self, question: str) -> list[dict[str, Any]]:
        return self.vector_db.search_similar_chunks(question, top_k=settings.TOP_K)

    def build_context(self, chunks: list[dict[str, Any]]) -> str:
        if not chunks:
            return ""
        return "\n\n".join([chunk["text"] for chunk in chunks])

    def ask_question(self, question: str) -> dict[str, Any]:
        context_chunks = self.retrieve_context(question)
        context = self.build_context(context_chunks)
        print("*"*50)
        print(context_chunks)
        print(context)
        print("*"*50)
        llm_response = self.llm_service.generate_response(context=context, question=question)
        sources = [
            {"file": chunk["metadata"].get("source", "unknown"), "page": chunk["metadata"].get("page", "")}
            for chunk in context_chunks
        ]
        return {
            "answer": llm_response["answer"],
            "sources": sources,
            "chunks_used": len(context_chunks),
        }

import logging
from typing import Any

from langchain_chroma import Chroma

from config.settings import settings
from utils.vectorEmbeddingService import get_embeddings

logger = logging.getLogger(__name__)


class VectorDbService:
    def __init__(self) -> None:
        self.vector_store = Chroma(
            collection_name=settings.COLLECTION_NAME,
            embedding_function=get_embeddings(),
            persist_directory=settings.CHROMA_PATH,
        )

    def insert_chunks(self, chunks: list[dict[str, Any]], document_id: str, source: str, file_type: str, uploaded_at: str) -> None:
        for chunk in chunks:
            text = chunk["text"]
            metadata = {
                "document_id": document_id,
                "source": source,
                "page": chunk.get("page", ""),
                "chunk_id": chunk["chunk_id"],
                "file_type": file_type,
                "uploaded_at": uploaded_at,
            }
            self.vector_store.add_texts(
                texts=[text],
                metadatas=[metadata],
            )

    def search_similar_chunks(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        docs = self.vector_store.similarity_search_with_score(query, k=top_k)
        results: list[dict[str, Any]] = []
        for doc, score in docs:
            results.append(
                {
                    "page": doc.metadata.get("page", ""),
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score,
                }
            )
        return results

    def delete_document(self, document_id: str) -> None:
        self.vector_store.delete(where={"document_id": document_id})

    def get_document(self, document_id: str) -> list[dict[str, Any]]:
        docs = self.vector_store.get(where={"document_id": document_id})
        return docs.get("documents", [])

    def list_documents(self) -> list[dict[str, Any]]:
        return self.vector_store.get().get("metadatas", [])

    def update_document(self, document_id: str, chunks: list[dict[str, Any]], source: str, file_type: str, uploaded_at: str) -> None:
        self.delete_document(document_id)
        self.insert_chunks(chunks, document_id, source, file_type, uploaded_at)

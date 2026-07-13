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

    def insert_chunks(
        self,
        chunks: list[dict[str, Any]],
        document_id: str,
        source: str,
        file_type: str,
        uploaded_at: str,
        document_role: str = "applicant",
        industry: str | None = None,
    ) -> None:
        for chunk in chunks:
            text = chunk["text"]
            metadata = {
                "document_id": document_id,
                "source": source,
                "page": chunk.get("page", ""),
                "chunk_id": chunk["chunk_id"],
                "file_type": file_type,
                "uploaded_at": uploaded_at,
                "document_role": document_role,
                "industry": (industry or "").strip().lower(),
            }
            self.vector_store.add_texts(
                texts=[text],
                metadatas=[metadata],
            )

    def search_similar_chunks(self, query: str, top_k: int = 5, where: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        if where:
            docs = self.vector_store.similarity_search_with_score(query, k=top_k, filter=where)
        else:
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

    def list_document_index(self, document_role: str | None = None) -> list[dict[str, Any]]:
        where = {"document_role": document_role} if document_role else None
        docs = self.vector_store.get(where=where)
        metadatas = docs.get("metadatas", [])

        index: dict[str, dict[str, Any]] = {}
        for metadata in metadatas:
            document_id = str(metadata.get("document_id", ""))
            if not document_id:
                continue
            if document_id not in index:
                index[document_id] = {
                    "document_id": document_id,
                    "source": metadata.get("source", "unknown"),
                    "document_role": metadata.get("document_role", ""),
                    "industry": metadata.get("industry", ""),
                    "uploaded_at": metadata.get("uploaded_at", ""),
                }
        return list(index.values())

    def guideline_exists(self, source: str, industry: str) -> bool:
        docs = self.vector_store.get(
            where={
                "$and": [
                    {"document_role": "guideline"},
                    {"source": source},
                    {"industry": industry.strip().lower()},
                ]
            },
            limit=1,
        )
        return bool(docs.get("ids"))

    def document_exists(self, source: str, document_role: str, industry: str | None = None) -> bool:
        conditions: list[dict[str, Any]] = [
            {"document_role": document_role},
            {"source": source},
        ]
        if industry is not None:
            conditions.append({"industry": industry.strip().lower()})

        docs = self.vector_store.get(where={"$and": conditions}, limit=1)
        return bool(docs.get("ids"))

    def update_document(
        self,
        document_id: str,
        chunks: list[dict[str, Any]],
        source: str,
        file_type: str,
        uploaded_at: str,
        document_role: str = "applicant",
        industry: str | None = None,
    ) -> None:
        self.delete_document(document_id)
        self.insert_chunks(chunks, document_id, source, file_type, uploaded_at, document_role=document_role, industry=industry)

from __future__ import annotations

from typing import Any


class ChunkingService:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> list[dict[str, Any]]:
        if not text.strip():
            return []

        chunks: list[dict[str, Any]] = []
        start = 0
        index = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end]
            chunks.append({"chunk_id": f"chunk_{index}", "text": chunk_text})
            if end >= len(text):
                break
            start = max(0, end - self.chunk_overlap)
            index += 1

        return chunks

    def chunk_pages(self, pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        chunks: list[dict[str, Any]] = []
        for page in pages:
            page_number = page.get("page", 0)
            content = str(page.get("content", ""))
            for chunk in self.chunk_text(content):
                chunk["page"] = page_number
                chunks.append(chunk)
        return chunks

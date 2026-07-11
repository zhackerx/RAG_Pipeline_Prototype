import logging
import uuid
from pathlib import Path
from typing import Any

from config.settings import settings
from utils.chunkingService import ChunkingService
from utils.markdownLoader import MarkdownLoader
from utils.pdfLoader import PDFLoader
from services.vectorDbService import VectorDbService

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self) -> None:
        self.vector_db = VectorDbService()
        self.chunking_service = ChunkingService(settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def upload_pdf(self, file_path: str | Path, document_name: str | None = None) -> dict[str, Any]:
        source_path = Path(file_path)
        document_id = str(uuid.uuid4())
        destination = self.upload_dir / f"{document_id}_{source_path.name}"
        destination.write_bytes(source_path.read_bytes())

        loader = PDFLoader(destination)
        pages = loader.load()
        chunks = self.chunking_service.chunk_pages(pages)

        for chunk in chunks:
            chunk["document_id"] = document_id

        self.vector_db.insert_chunks(
            chunks=chunks,
            document_id=document_id,
            source=source_path.name,
            file_type="pdf",
            uploaded_at=str(Path(destination).stat().st_mtime),
        )
        return {"document_id": document_id, "source": source_path.name, "chunks": len(chunks)}

    def upload_markdown(self, file_path: str | Path, document_name: str | None = None) -> dict[str, Any]:
        source_path = Path(file_path)
        document_id = str(uuid.uuid4())
        destination = self.upload_dir / f"{document_id}_{source_path.name}"
        destination.write_bytes(source_path.read_bytes())

        loader = MarkdownLoader(destination)
        text = loader.load()
        chunks = self.chunking_service.chunk_text(text)

        for chunk in chunks:
            chunk["document_id"] = document_id

        self.vector_db.insert_chunks(
            chunks=chunks,
            document_id=document_id,
            source=source_path.name,
            file_type="markdown",
            uploaded_at=str(Path(destination).stat().st_mtime),
        )
        return {"document_id": document_id, "source": source_path.name, "chunks": len(chunks)}

    def reindex_document(self, document_id: str, file_path: str | Path) -> dict[str, Any]:
        self.vector_db.delete_document(document_id)
        source_path = Path(file_path)
        if source_path.suffix.lower() == ".pdf":
            return self.upload_pdf(source_path, document_id)
        return self.upload_markdown(source_path, document_id)

    def delete_document(self, document_id: str) -> None:
        self.vector_db.delete_document(document_id)

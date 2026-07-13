import logging
import uuid
from pathlib import Path
from typing import Any

from config.settings import settings
from utils.chunkingService import ChunkingService
from utils.excelLoader import ExcelLoader
from utils.markdownLoader import MarkdownLoader
from utils.pdfLoader import PDFLoader
from utils.securityMaskingService import SecurityMaskingService
from services.vectorDbService import VectorDbService

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self) -> None:
        self.vector_db = VectorDbService()
        self.chunking_service = ChunkingService(settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
        self.masking_service = SecurityMaskingService()
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _persist_source(self, file_path: str | Path) -> tuple[str, Path, Path]:
        source_path = Path(file_path)
        document_id = str(uuid.uuid4())
        destination = self.upload_dir / f"{document_id}_{source_path.name}"
        destination.write_bytes(source_path.read_bytes())
        return document_id, source_path, destination

    def upload_pdf(
        self,
        file_path: str | Path,
        document_name: str | None = None,
        document_role: str = "applicant",
        industry: str | None = None,
    ) -> dict[str, Any]:
        document_id, source_path, destination = self._persist_source(file_path)

        loader = PDFLoader(destination)
        pages = loader.load()
        for page in pages:
            masked = self.masking_service.mask_text(str(page.get("content", "")))
            page["content"] = masked["text"]
        chunks = self.chunking_service.chunk_pages(pages)

        for chunk in chunks:
            chunk["document_id"] = document_id

        self.vector_db.insert_chunks(
            chunks=chunks,
            document_id=document_id,
            source=source_path.name,
            file_type="pdf",
            uploaded_at=str(Path(destination).stat().st_mtime),
            document_role=document_role,
            industry=industry,
        )
        return {
            "document_id": document_id,
            "source": source_path.name,
            "chunks": len(chunks),
            "document_role": document_role,
            "industry": (industry or "").strip().lower(),
        }

    def upload_markdown(
        self,
        file_path: str | Path,
        document_name: str | None = None,
        document_role: str = "applicant",
        industry: str | None = None,
    ) -> dict[str, Any]:
        document_id, source_path, destination = self._persist_source(file_path)

        loader = MarkdownLoader(destination)
        text = loader.load()
        masked = self.masking_service.mask_text(text)
        text = masked["text"]
        chunks = self.chunking_service.chunk_text(text)

        for chunk in chunks:
            chunk["document_id"] = document_id

        self.vector_db.insert_chunks(
            chunks=chunks,
            document_id=document_id,
            source=source_path.name,
            file_type="markdown",
            uploaded_at=str(Path(destination).stat().st_mtime),
            document_role=document_role,
            industry=industry,
        )
        return {
            "document_id": document_id,
            "source": source_path.name,
            "chunks": len(chunks),
            "document_role": document_role,
            "industry": (industry or "").strip().lower(),
        }

    def upload_excel(
        self,
        file_path: str | Path,
        document_role: str = "guideline",
        industry: str | None = None,
    ) -> dict[str, Any]:
        document_id, source_path, destination = self._persist_source(file_path)

        loader = ExcelLoader(destination)
        text = loader.load_as_text()
        masked = self.masking_service.mask_text(text)
        text = masked["text"]
        chunks = self.chunking_service.chunk_text(text)

        for chunk in chunks:
            chunk["document_id"] = document_id

        self.vector_db.insert_chunks(
            chunks=chunks,
            document_id=document_id,
            source=source_path.name,
            file_type="excel",
            uploaded_at=str(Path(destination).stat().st_mtime),
            document_role=document_role,
            industry=industry,
        )
        return {
            "document_id": document_id,
            "source": source_path.name,
            "chunks": len(chunks),
            "document_role": document_role,
            "industry": (industry or "").strip().lower(),
        }

    def reindex_document(self, document_id: str, file_path: str | Path) -> dict[str, Any]:
        self.vector_db.delete_document(document_id)
        source_path = Path(file_path)
        if source_path.suffix.lower() == ".pdf":
            return self.upload_pdf(source_path, document_id)
        if source_path.suffix.lower() in {".xlsx", ".xlsm", ".xltx", ".xltm"}:
            return self.upload_excel(source_path)
        return self.upload_markdown(source_path, document_id)

    def delete_document(self, document_id: str) -> None:
        self.vector_db.delete_document(document_id)

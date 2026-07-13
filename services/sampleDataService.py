import logging
from pathlib import Path

from config.settings import settings
from services.documentService import DocumentService

logger = logging.getLogger(__name__)


class SampleDataService:
    def __init__(self) -> None:
        self.document_service = DocumentService()

    def seed(self) -> dict[str, int]:
        root = Path(settings.SAMPLE_DATA_DIR)
        if not root.exists() or not root.is_dir():
            logger.info("Sample data directory not found: %s", root)
            return {"seeded": 0, "skipped": 0}

        seeded = 0
        skipped = 0

        for file_path in root.rglob("*"):
            if not file_path.is_file() or file_path.suffix.lower() not in {".md", ".markdown", ".pdf", ".xlsx", ".xlsm", ".xltx", ".xltm"}:
                continue

            if self.document_service.vector_db.document_exists(
                source=file_path.name,
                document_role="applicant",
                industry=settings.TARGET_INDUSTRY,
            ):
                skipped += 1
                continue

            suffix = file_path.suffix.lower()
            if suffix == ".pdf":
                self.document_service.upload_pdf(file_path, document_role="applicant", industry=settings.TARGET_INDUSTRY)
            elif suffix in {".md", ".markdown"}:
                self.document_service.upload_markdown(file_path, document_role="applicant", industry=settings.TARGET_INDUSTRY)
            else:
                self.document_service.upload_excel(file_path, document_role="applicant", industry=settings.TARGET_INDUSTRY)
            seeded += 1

        logger.info("Sample applicant seed completed. Seeded: %s, Skipped: %s", seeded, skipped)
        return {"seeded": seeded, "skipped": skipped}

import logging
from pathlib import Path

from config.settings import settings
from services.documentService import DocumentService

logger = logging.getLogger(__name__)


class GuidelineBootstrapService:
    SUPPORTED_EXTENSIONS = {".pdf", ".md", ".markdown", ".xlsx", ".xlsm", ".xltx", ".xltm"}

    def __init__(self) -> None:
        self.document_service = DocumentService()

    def bootstrap(self) -> dict[str, int]:
        root = Path(settings.GUIDELINES_DIR)
        if not root.exists() or not root.is_dir():
            logger.info("Guidelines directory not found: %s", root)
            return {"indexed": 0, "skipped": 0}

        indexed = 0
        skipped = 0

        for file_path in root.rglob("*"):
            if not file_path.is_file() or file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue

            industry = self._infer_industry(root, file_path)
            if industry != settings.TARGET_INDUSTRY:
                skipped += 1
                continue
            if self.document_service.vector_db.guideline_exists(file_path.name, industry):
                skipped += 1
                continue

            suffix = file_path.suffix.lower()
            if suffix == ".pdf":
                self.document_service.upload_pdf(file_path, document_role="guideline", industry=industry)
            elif suffix in {".md", ".markdown"}:
                self.document_service.upload_markdown(file_path, document_role="guideline", industry=industry)
            else:
                self.document_service.upload_excel(file_path, document_role="guideline", industry=industry)
            indexed += 1

        logger.info("Guideline bootstrap complete. Indexed: %s, Skipped: %s", indexed, skipped)
        return {"indexed": indexed, "skipped": skipped}

    def _infer_industry(self, root: Path, file_path: Path) -> str:
        relative_parent = file_path.parent.relative_to(root)
        if str(relative_parent) == ".":
            return settings.TARGET_INDUSTRY
        return relative_parent.parts[0].strip().lower() or "general"

from pathlib import Path
from typing import Any

from config.settings import settings
from services.llmService import LLMService
from services.vectorDbService import VectorDbService
from utils.pdfLoader import PDFLoader


class RiskAssessmentService:
    SAMPLE_GUIDELINE_CONTEXT = """
FSSAI Food Processing Advisory Baseline
1. FSSAI license validity and category fitment must be verified.
2. Repeated food safety non-compliance notices increase risk.
3. Absence of batch traceability and recall process is high risk.
4. Inadequate hygiene/sanitation controls increase operational risk.
5. Unstable raw material quality controls increase rejection risk.
6. Strong QA records, audit readiness, and compliant labeling reduce risk.
""".strip()

    def __init__(self) -> None:
        self.vector_db = VectorDbService()
        self.llm = LLMService()

    def _load_applicant_text(self, file_path: str | Path) -> str:
        loader = PDFLoader(file_path)
        pages = loader.load()
        return "\n\n".join(str(page.get("content", "")) for page in pages)

    def _get_guideline_context(self, industry: str, applicant_text: str) -> tuple[str, list[dict[str, Any]]]:
        industry_filter = {"$and": [{"document_role": "guideline"}, {"industry": settings.TARGET_INDUSTRY}]}

        chunks = self.vector_db.search_similar_chunks(
            applicant_text,
            top_k=settings.TOP_K,
            where=industry_filter,
        )

        if not chunks:
            chunks = self.vector_db.search_similar_chunks(
                applicant_text,
                top_k=settings.TOP_K,
                where=industry_filter,
            )

        if not chunks:
            return self.SAMPLE_GUIDELINE_CONTEXT, []

        context = "\n\n".join(chunk["text"] for chunk in chunks)
        return context, chunks

    def assess_text(self, applicant_text: str, industry_override: str | None = None) -> dict[str, Any]:
        industry = settings.TARGET_INDUSTRY
        guideline_context, guideline_chunks = self._get_guideline_context(industry, applicant_text)

        result = self.llm.generate_risk_assessment(
            industry=industry,
            applicant_text=applicant_text,
            guideline_context=guideline_context,
        )

        if guideline_chunks:
            result["guideline_sources"] = [
                {
                    "file": chunk["metadata"].get("source", "unknown"),
                    "page": chunk["metadata"].get("page", ""),
                    "industry": chunk["metadata"].get("industry", ""),
                }
                for chunk in guideline_chunks
            ]
        else:
            result["guideline_sources"] = [
                {
                    "file": "sample_internal_guideline",
                    "page": "",
                    "industry": industry,
                }
            ]

        result["guideline_chunks_used"] = len(guideline_chunks)
        return result

    def assess_pdf(self, file_path: str | Path) -> dict[str, Any]:
        applicant_text = self._load_applicant_text(file_path)
        return self.assess_text(applicant_text)

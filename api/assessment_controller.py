import logging
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from models.risk_assessment_request import RiskAssessmentRequest
from models.risk_assessment_response import RiskAssessmentResponse
from services.riskAssessmentService import RiskAssessmentService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/assessment", tags=["assessment"])
risk_service = RiskAssessmentService()


@router.post("/upload/pdf", response_model=RiskAssessmentResponse, status_code=status.HTTP_200_OK)
async def assess_uploaded_pdf(file: UploadFile = File(...)) -> RiskAssessmentResponse:
    try:
        temp_path = Path(f"./uploads/{file.filename}")
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        contents = await file.read()
        temp_path.write_bytes(contents)

        result = risk_service.assess_pdf(temp_path)
        return RiskAssessmentResponse(**result)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Risk assessment failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/prototype", response_model=RiskAssessmentResponse, status_code=status.HTTP_200_OK)
async def assess_prototype(request: RiskAssessmentRequest) -> RiskAssessmentResponse:
    try:
        result = risk_service.assess_text(
            applicant_text=request.applicant_profile,
            industry_override=request.industry,
        )
        return RiskAssessmentResponse(**result)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Prototype risk assessment failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

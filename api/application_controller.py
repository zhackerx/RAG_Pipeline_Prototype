import logging
from typing import cast

from fastapi import APIRouter, HTTPException, status

from config.settings import settings
from models.application_request import ApplicationRequest
from models.risk_assessment_response import RiskAssessmentResponse
from services.riskAssessmentService import RiskAssessmentService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/application", tags=["application"])
risk_service: RiskAssessmentService | None = None


def get_risk_service() -> RiskAssessmentService:
    global risk_service
    if risk_service is None:
        risk_service = RiskAssessmentService()
    return cast(RiskAssessmentService, risk_service)


@router.post("/submit", response_model=RiskAssessmentResponse, status_code=status.HTTP_200_OK)
async def submit_application(request: ApplicationRequest) -> RiskAssessmentResponse:
    try:
        applicant_profile = (
            f"Industry: {settings.TARGET_INDUSTRY}. "
            f"Business Name: {request.business_name}. "
            f"Promoter: {request.promoter_name}. "
            f"Annual Turnover: {request.annual_turnover_crore} crore. "
            f"DSCR: {request.dscr}. "
            f"GST delays: {request.gst_delay_months} months. "
            f"Top customer revenue share: {request.top_customer_revenue_percent} percent. "
            f"Working capital cycle: {request.working_capital_days} days. "
            f"Overdues 90+ days: {request.existing_overdues_90_plus}. "
            f"Notes: {request.notes}"
        )
        result = get_risk_service().assess_text(applicant_profile, industry_override=settings.TARGET_INDUSTRY)
        return RiskAssessmentResponse(**result)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Application submission failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

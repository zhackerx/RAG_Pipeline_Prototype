from pydantic import BaseModel, Field


class RiskAssessmentRequest(BaseModel):
    applicant_profile: str = Field(..., min_length=10, description="Applicant details as plain text")
    industry: str | None = Field(default=None, description="Optional override industry")

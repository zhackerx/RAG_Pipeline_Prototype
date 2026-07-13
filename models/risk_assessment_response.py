from pydantic import BaseModel, Field


class RiskAssessmentResponse(BaseModel):
    industry: str = Field(default="general")
    risk_score: int = Field(default=50, ge=0, le=100)
    risk_level: str = Field(default="MEDIUM")
    summary: str = Field(default="")
    key_risk_factors: list[str] = Field(default_factory=list)
    advisory_notes: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    guideline_sources: list[dict[str, object]] = Field(default_factory=list)
    guideline_chunks_used: int = Field(default=0)
    security: dict[str, object] = Field(default_factory=dict)

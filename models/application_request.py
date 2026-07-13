from pydantic import BaseModel, Field


class ApplicationRequest(BaseModel):
    business_name: str = Field(..., min_length=2)
    promoter_name: str = Field(..., min_length=2)
    annual_turnover_crore: float = Field(..., ge=0)
    dscr: float = Field(..., ge=0)
    gst_delay_months: int = Field(default=0, ge=0)
    top_customer_revenue_percent: float = Field(default=0, ge=0, le=100)
    working_capital_days: int = Field(default=0, ge=0)
    existing_overdues_90_plus: bool = Field(default=False)
    notes: str = Field(default="")

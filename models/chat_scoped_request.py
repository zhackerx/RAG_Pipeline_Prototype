from pydantic import BaseModel, Field


class ChatScopedRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Officer question for policy and applicant context")
    applicant_document_ids: list[str] = Field(default_factory=list, description="Applicant document ids to scope retrieval")

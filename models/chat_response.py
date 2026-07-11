from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    answer: str = Field(..., description="Generated answer")
    sources: list[dict[str, object]] = Field(default_factory=list, description="List of cited sources")
    chunks_used: int = Field(default=0, description="Number of retrieved chunks used")

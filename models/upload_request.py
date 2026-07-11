from typing import Literal

from pydantic import BaseModel, Field


class UploadRequest(BaseModel):
    document_name: str | None = Field(default=None, description="Optional custom document name")
    file_type: Literal["pdf", "markdown"] = Field(default="pdf", description="Document type")

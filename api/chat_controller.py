import logging
from typing import cast

from fastapi import APIRouter, HTTPException, status

from models.chat_request import ChatRequest
from models.chat_response import ChatResponse
from models.chat_scoped_request import ChatScopedRequest
from services.ragService import RAGService
from services.llmService import LLMTemporarilyUnavailableError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])
rag_service: RAGService | None = None


def get_rag_service() -> RAGService:
    global rag_service
    if rag_service is None:
        rag_service = RAGService()
    return cast(RAGService, rag_service)


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        result = get_rag_service().ask_question(request.question)
        return ChatResponse(**result)
    except LLMTemporarilyUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Chat request failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/scoped", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_scoped(request: ChatScopedRequest) -> ChatResponse:
    try:
        result = get_rag_service().ask_question_scoped(
            question=request.question,
            applicant_document_ids=request.applicant_document_ids,
        )
        return ChatResponse(**result)
    except LLMTemporarilyUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Scoped chat request failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

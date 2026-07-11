import logging

from fastapi import APIRouter, HTTPException, status

from models.chat_request import ChatRequest
from models.chat_response import ChatResponse
from services.ragService import RAGService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])
rag_service = RAGService()


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        result = rag_service.ask_question(request.question)
        return ChatResponse(**result)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Chat request failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

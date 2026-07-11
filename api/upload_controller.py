import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from services.documentService import DocumentService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])
document_service = DocumentService()


@router.post("/upload/pdf", status_code=status.HTTP_201_CREATED)
async def upload_pdf(file: UploadFile = File(...)) -> dict[str, Any]:
    try:
        temp_path = Path(f"./uploads/{file.filename}")
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        contents = await file.read()
        temp_path.write_bytes(contents)
        result = document_service.upload_pdf(temp_path)
        return {"message": "PDF uploaded successfully", **result}
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("PDF upload failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/upload/markdown", status_code=status.HTTP_201_CREATED)
async def upload_markdown(file: UploadFile = File(...)) -> dict[str, Any]:
    try:
        temp_path = Path(f"./uploads/{file.filename}")
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        contents = await file.read()
        temp_path.write_bytes(contents)
        result = document_service.upload_markdown(temp_path)
        return {"message": "Markdown uploaded successfully", **result}
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Markdown upload failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(document_id: str) -> dict[str, str]:
    document_service.delete_document(document_id)
    return {"message": "Document deleted successfully", "document_id": document_id}


@router.put("/{document_id}", status_code=status.HTTP_200_OK)
async def reindex_document(document_id: str, file: UploadFile = File(...)) -> dict[str, Any]:
    try:
        temp_path = Path(f"./uploads/{file.filename}")
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        contents = await file.read()
        temp_path.write_bytes(contents)
        result = document_service.reindex_document(document_id, temp_path)
        return {"message": "Document re-indexed successfully", **result}
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Document re-indexing failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("", status_code=status.HTTP_200_OK)
async def list_documents() -> list[dict[str, Any]]:
    return document_service.vector_db.list_documents()


@router.get("/{document_id}", status_code=status.HTTP_200_OK)
async def get_document(document_id: str) -> dict[str, Any]:
    return {"document_id": document_id, "chunks": document_service.vector_db.get_document(document_id)}

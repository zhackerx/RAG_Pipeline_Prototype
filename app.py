import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.chat_controller import router as chat_router
from api.upload_controller import router as upload_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("rag_app")


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting RAG application")
    yield
    logger.info("Stopping RAG application")


app = FastAPI(
    title="RAG Document Assistant",
    version="1.0.0",
    description="Production-ready retrieval augmented generation backend with Gemini and ChromaDB",
    lifespan=lifespan,
)

app.include_router(upload_router)
app.include_router(chat_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "rag-api"}

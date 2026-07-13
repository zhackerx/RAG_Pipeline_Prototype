import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.assessment_controller import router as assessment_router
from api.chat_controller import router as chat_router
from api.upload_controller import router as upload_router
from config.settings import settings
from services.guidelineBootstrapService import GuidelineBootstrapService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("rag_app")


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting RAG application")
    if settings.AUTO_INDEX_GUIDELINES:
        bootstrap = GuidelineBootstrapService()
        stats = bootstrap.bootstrap()
        logger.info("Guideline preload completed: %s", stats)
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
app.include_router(assessment_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "rag-api"}

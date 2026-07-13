import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.application_controller import router as application_router
from api.assessment_controller import router as assessment_router
from api.chat_controller import router as chat_router
from api.upload_controller import router as upload_router
from config.settings import settings
from services.guidelineBootstrapService import GuidelineBootstrapService
from services.sampleDataService import SampleDataService

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
    if settings.AUTO_SEED_SAMPLE_DATA:
        sample_service = SampleDataService()
        sample_stats = sample_service.seed()
        logger.info("Sample data preload completed: %s", sample_stats)
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
app.include_router(application_router)

frontend_dir = Path(__file__).parent / "frontend"
app.mount("/frontend", StaticFiles(directory=str(frontend_dir)), name="frontend")


@app.get("/")
async def home() -> FileResponse:
    return FileResponse(frontend_dir / "index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "rag-api"}

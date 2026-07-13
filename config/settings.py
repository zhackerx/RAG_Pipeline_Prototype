from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    GEMINI_API_KEY: str
    CHROMA_PATH: str = "./chroma_storage"
    UPLOAD_DIR: str = "./uploads"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K: int = 5
    GEMINI_LLM_MODEL: str = "gemini-3.5-flash" #gemini-3.5-flash
    EMBEDDING_MODEL: str = "models/gemini-embedding-001"
    COLLECTION_NAME: str = "rag_documents"
    GUIDELINES_DIR: str = "./guidelines"
    AUTO_INDEX_GUIDELINES: bool = True
    TARGET_INDUSTRY: str = "food_processing"
    TARGET_GUIDELINE_STANDARD: str = "fssai"


settings = Settings()

import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Multimodal Enterprise Document RAG"
    VERSION: str = "1.0.0"
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "data/documents")
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "data/chroma_db")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "multimodal_docs")
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", 4))
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

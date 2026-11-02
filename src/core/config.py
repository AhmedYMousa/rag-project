from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        # Prefix is used to bind .env and enviroemnt variables to props of Settings class by their name
        env_prefix="RAG_",
        # RAG_LOG_LEVEL will bind to => log_level
    )
    app_name: str = "rag-api"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    qdrant_url: str
    qdrant_collection: str
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    max_upload_mb: int = 20
    allowed_file_extensions: list[str] = [".pdf", ".md"]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

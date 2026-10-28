from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="RAG_"  # Prefix is used to bind .env and enviroemnt variables to props of Settings class by their name
        # RAG_LOG_LEVEL will bind to => log_level
    )
    app_name: str = "rag-api"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
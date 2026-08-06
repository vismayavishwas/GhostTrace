import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """GhostTrace AI System Settings."""
    
    PROJECT_NAME: str = "GhostTrace AI Backend"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Intent Disambiguation Settings
    AUTO_APPROVE_THRESHOLD: float = 0.85
    
    # Google Gemini API Settings
    GEMINI_API_KEY: str = ""
    VERTEX_AI_PROJECT: str = "ghosttrace-ai-dev"

    VERTEX_AI_LOCATION: str = "us-central1"
    
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

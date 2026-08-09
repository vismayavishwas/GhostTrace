from typing import List, Any, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """GhostTrace AI System Settings."""
    
    PROJECT_NAME: str = "GhostTrace AI Backend"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "*"]
    
    # Intent Disambiguation Settings
    AUTO_APPROVE_THRESHOLD: float = 0.85
    
    # Google Gemini API Settings
    GEMINI_API_KEY: str = ""
    VERTEX_AI_PROJECT: str = "ghosttrace-ai-dev"
    VERTEX_AI_LOCATION: str = "us-central1"
    
    LOG_LEVEL: str = "INFO"

    @field_validator("PORT", mode="before")
    @classmethod
    def parse_port(cls, v: Any) -> int:
        if v is None or v == "" or (isinstance(v, str) and not v.strip()):
            return 8000
        try:
            return int(v)
        except (ValueError, TypeError):
            return 8000

    @field_validator("AUTO_APPROVE_THRESHOLD", mode="before")
    @classmethod
    def parse_threshold(cls, v: Any) -> float:
        if v is None or v == "" or (isinstance(v, str) and not v.strip()):
            return 0.85
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.85

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            if not v.strip():
                return ["*"]
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [x.strip() for x in v.split(",") if x.strip()]
        return v or ["*"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

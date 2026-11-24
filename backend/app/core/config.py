"""Application Configuration and Environment Settings."""

import json
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """DevPilot application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "DevPilot"
    APP_VERSION: str = "0.1.0-beta"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # Security
    JWT_SECRET_KEY: str = "devpilot-insecure-secret-key-change-in-production-min32"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    # Database (PostgreSQL or SQLite)
    DATABASE_URL: str = "sqlite:///./devpilot.db"

    # Cache and Queues (Redis)
    REDIS_URL: str = "redis://localhost:6381/0"
    CELERY_BROKER_URL: str = "redis://localhost:6381/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6381/2"

    # AI Providers (Future Phases)
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    AI_CHAT_PROVIDER: str = "openai"
    AI_EMBEDDING_PROVIDER: str = "local"
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    GEMINI_CHAT_MODEL: str = "gemini-1.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"
    VECTOR_DB_PATH: str = "./.devpilot_vector.db"
    RAG_TOP_K: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.0
    RAG_MAX_CONTEXT_CHARS: int = 12000

    # GitHub Integration
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_CALLBACK_URL: str = "http://localhost:8000/api/v1/github/callback"
    GITHUB_REDIRECT_URI: str = "http://localhost:5173/auth/callback"
    GITHUB_WEBHOOK_SECRET: str = ""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()


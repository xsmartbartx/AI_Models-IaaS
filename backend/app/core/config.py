import os
from typing import List
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    SECRET_KEY: str = "aifactory-secret-key-change-in-production"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    MEDIA_ROOT: str = "/app/media"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://frontend:3000",
    ]

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://aifactory:aifactory_secret@postgres:5432/aifactory"
    DATABASE_URL_SYNC: str = "postgresql://aifactory:aifactory_secret@postgres:5432/aifactory"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"

    # AI Services
    COMFYUI_URL: str = "http://comfyui:8188"
    OLLAMA_URL: str = "http://ollama:11434"

    # LLM
    LLM_MODEL: str = "qwen2.5:7b"

    # Image generation defaults
    DEFAULT_IMAGE_WIDTH: int = 768
    DEFAULT_IMAGE_HEIGHT: int = 1024
    DEFAULT_IMAGE_STEPS: int = 25
    DEFAULT_IMAGE_CFG: float = 7.0

    # Video generation defaults
    DEFAULT_VIDEO_FRAMES: int = 25
    DEFAULT_VIDEO_WIDTH: int = 512
    DEFAULT_VIDEO_HEIGHT: int = 512

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
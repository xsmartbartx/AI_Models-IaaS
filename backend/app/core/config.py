from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # App
    SECRET_KEY: str = "aifactory-secret-key-change-in-production"
    ENVIRONMENT: str = "development"
    MEDIA_ROOT: str = "/app/media"

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

    model_config = {"env_file": ".env", "extra": "allow"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
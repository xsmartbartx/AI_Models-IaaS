"""
AI Influencer Factory - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from backend.app.core.config import get_settings
from backend.app.core.database import init_db, close_db
from backend.app.api import characters, images, videos, posts, prompt_templates, health

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    await init_db()
    os.makedirs(os.path.join(settings.MEDIA_ROOT, "images"), exist_ok=True)
    os.makedirs(os.path.join(settings.MEDIA_ROOT, "videos"), exist_ok=True)
    yield
    await close_db()


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Influencer Factory",
        description="Zero-budget platform for generating virtual AI influencers and content",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Serve generated media files
    media_dir = settings.MEDIA_ROOT
    if os.path.exists(media_dir):
        app.mount("/media", StaticFiles(directory=media_dir), name="media")

    # Include routers
    api_prefix = settings.API_V1_PREFIX
    app.include_router(health.router, tags=["health"])
    app.include_router(characters.router, prefix=api_prefix)
    app.include_router(images.router, prefix=api_prefix)
    app.include_router(videos.router, prefix=api_prefix)
    app.include_router(posts.router, prefix=api_prefix)
    app.include_router(prompt_templates.router, prefix=api_prefix)

    return app


app = create_app()
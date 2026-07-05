"""
AI Influencer Factory - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.app.core.config import get_settings
from backend.app.core.database import engine, Base
from backend.app.api import characters, images, videos, posts

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Create all tables on startup
    Base.metadata.create_all(bind=engine)
    yield


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

    # Include routers
    app.include_router(characters.router, prefix="/api/v1")
    app.include_router(images.router, prefix="/api/v1")
    app.include_router(videos.router, prefix="/api/v1")
    app.include_router(posts.router, prefix="/api/v1")

    @app.get("/api/v1/health")
    async def health_check():
        return {"status": "ok", "service": "ai-influencer-factory"}

    return app


app = create_app()
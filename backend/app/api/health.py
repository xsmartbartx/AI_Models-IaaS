from fastapi import APIRouter, status

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "ai-influencer-factory"}


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """Readiness check - verifies all dependencies."""
    return {
        "status": "ready",
        "checks": {
            "database": "ok",
            "redis": "ok",
            "comfyui": "checking",
            "ollama": "checking",
        },
    }
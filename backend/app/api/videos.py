from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.video import Video
from app.models.character import Character
from app.models.image import Image
from app.schemas.video import (
    VideoGenerateRequest,
    VideoResponse,
    VideoListResponse,
)
from app.tasks.generation_tasks import generate_video_task

router = APIRouter(prefix="/videos", tags=["videos"])


@router.get("/", response_model=VideoListResponse)
async def list_videos(
    character_id: Optional[UUID] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
):
    """List videos, optionally filtered by character or status."""
    query = select(Video).order_by(Video.created_at.desc())

    if character_id:
        query = query.filter(Video.character_id == character_id)
    if status_filter:
        query = query.filter(Video.status == status_filter)

    result = await db.execute(query)
    videos = result.scalars().all()
    return VideoListResponse(
        items=[VideoResponse.model_validate(v) for v in videos],
        total=len(videos),
    )


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(video_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single video by ID."""
    result = await db.execute(select(Video).filter(Video.id == video_id))
    vid = result.scalar_one_or_none()
    if not vid:
        raise HTTPException(status_code=404, detail="Video not found")
    return VideoResponse.model_validate(vid)


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_video(data: VideoGenerateRequest, db: AsyncSession = Depends(get_db)):
    """Queue a video generation task. Runs async via Celery."""
    # Validate character exists
    result = await db.execute(select(Character).filter(Character.id == data.character_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Character not found")

    # Resolve image path if source_image_id provided
    image_path = ""
    if data.source_image_id:
        img_result = await db.execute(select(Image).filter(Image.id == data.source_image_id))
        img = img_result.scalar_one_or_none()
        if img:
            image_path = img.file_path

    task = generate_video_task.delay(
        character_id=str(data.character_id),
        image_path=image_path,
        prompt=data.prompt or "smooth cinematic motion, natural movement",
    )
    return {"status": "processing", "task_id": task.id, "message": "Video generation queued"}


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(video_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a video record."""
    result = await db.execute(select(Video).filter(Video.id == video_id))
    vid = result.scalar_one_or_none()
    if not vid:
        raise HTTPException(status_code=404, detail="Video not found")
    await db.delete(vid)
    await db.flush()
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.video import Video
from backend.app.schemas.video import (
    VideoGenerateRequest,
    VideoResponse,
    VideoListResponse,
)
from backend.app.tasks.generation_tasks import generate_video_task

router = APIRouter(prefix="/videos", tags=["videos"])


@router.get("/", response_model=VideoListResponse)
def list_videos(character_id: UUID = None, db: Session = Depends(get_db)):
    """List videos, optionally filtered by character."""
    query = db.query(Video).order_by(Video.created_at.desc())
    if character_id:
        query = query.filter(Video.character_id == character_id)
    videos = query.all()
    return VideoListResponse(
        items=[VideoResponse.model_validate(v) for v in videos],
        total=len(videos),
    )


@router.get("/{video_id}", response_model=VideoResponse)
def get_video(video_id: UUID, db: Session = Depends(get_db)):
    """Get a single video by ID."""
    vid = db.query(Video).filter(Video.id == video_id).first()
    if not vid:
        raise HTTPException(status_code=404, detail="Video not found")
    return VideoResponse.model_validate(vid)


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
def generate_video(data: VideoGenerateRequest):
    """Queue a video generation task. Runs async via Celery."""
    task = generate_video_task.delay(
        character_id=str(data.character_id),
        image_path="",  # Will be resolved from source_image_id in the task
        prompt=data.prompt or "smooth cinematic motion, natural movement",
    )
    return {"status": "processing", "task_id": task.id}


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_video(video_id: UUID, db: Session = Depends(get_db)):
    """Delete a video record."""
    vid = db.query(Video).filter(Video.id == video_id).first()
    if not vid:
        raise HTTPException(status_code=404, detail="Video not found")
    db.delete(vid)
    db.commit()
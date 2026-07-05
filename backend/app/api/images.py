from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.image import Image
from backend.app.schemas.image import (
    ImageGenerateRequest,
    ImageResponse,
    ImageListResponse,
)
from backend.app.tasks.generation_tasks import generate_image_task

router = APIRouter(prefix="/images", tags=["images"])


@router.get("/", response_model=ImageListResponse)
def list_images(character_id: UUID = None, db: Session = Depends(get_db)):
    """List images, optionally filtered by character."""
    query = db.query(Image).order_by(Image.created_at.desc())
    if character_id:
        query = query.filter(Image.character_id == character_id)
    images = query.all()
    return ImageListResponse(
        items=[ImageResponse.model_validate(i) for i in images],
        total=len(images),
    )


@router.get("/{image_id}", response_model=ImageResponse)
def get_image(image_id: UUID, db: Session = Depends(get_db)):
    """Get a single image by ID."""
    img = db.query(Image).filter(Image.id == image_id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    return ImageResponse.model_validate(img)


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
def generate_image(data: ImageGenerateRequest):
    """Queue an image generation task. Runs async via Celery."""
    task = generate_image_task.delay(
        character_id=str(data.character_id),
        prompt=data.prompt or "beautiful lifestyle photo, natural lighting, realistic",
        negative_prompt=data.negative_prompt or "",
        category=data.category,
    )
    return {"status": "processing", "task_id": task.id}


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(image_id: UUID, db: Session = Depends(get_db)):
    """Delete an image record."""
    img = db.query(Image).filter(Image.id == image_id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    db.delete(img)
    db.commit()
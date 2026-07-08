from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models.image import Image
from backend.app.models.character import Character
from backend.app.schemas.image import (
    ImageGenerateRequest,
    ImageBatchGenerateRequest,
    ImageResponse,
    ImageListResponse,
)
from backend.app.tasks.generation_tasks import generate_image_task

router = APIRouter(prefix="/images", tags=["images"])


@router.get("/", response_model=ImageListResponse)
async def list_images(
    character_id: Optional[UUID] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List images, optionally filtered by character, status, or category."""
    query = select(Image).order_by(Image.created_at.desc())

    if character_id:
        query = query.filter(Image.character_id == character_id)
    if status_filter:
        query = query.filter(Image.status == status_filter)
    if category:
        query = query.filter(Image.category == category)

    result = await db.execute(query)
    images = result.scalars().all()
    return ImageListResponse(
        items=[ImageResponse.model_validate(i) for i in images],
        total=len(images),
    )


@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(image_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single image by ID."""
    result = await db.execute(select(Image).filter(Image.id == image_id))
    img = result.scalar_one_or_none()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    return ImageResponse.model_validate(img)


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_image(data: ImageGenerateRequest, db: AsyncSession = Depends(get_db)):
    """Queue a single image generation task. Runs async via Celery."""
    # Validate character exists
    result = await db.execute(select(Character).filter(Character.id == data.character_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Character not found")

    task = generate_image_task.delay(
        character_id=str(data.character_id),
        prompt=data.prompt or "beautiful lifestyle photo, natural lighting, realistic",
        negative_prompt=data.negative_prompt or "",
        category=data.category or "general",
    )
    return {"status": "processing", "task_id": task.id, "message": "Image generation queued"}


@router.post("/generate/batch", status_code=status.HTTP_202_ACCEPTED)
async def generate_image_batch(data: ImageBatchGenerateRequest, db: AsyncSession = Depends(get_db)):
    """Queue multiple image generation tasks in batch."""
    # Validate character exists
    result = await db.execute(select(Character).filter(Character.id == data.character_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Character not found")

    task_ids = []
    prompts = data.prompts or [data.prompt or "beautiful lifestyle photo, natural lighting, realistic"]

    for prompt in prompts:
        task = generate_image_task.delay(
            character_id=str(data.character_id),
            prompt=prompt,
            negative_prompt=data.negative_prompt or "",
            category=data.category or "general",
        )
        task_ids.append(task.id)

    return {
        "status": "processing",
        "task_ids": task_ids,
        "count": len(task_ids),
        "message": f"Queued {len(task_ids)} image generation tasks",
    }


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(image_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete an image record."""
    result = await db.execute(select(Image).filter(Image.id == image_id))
    img = result.scalar_one_or_none()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    await db.delete(img)
    await db.flush()
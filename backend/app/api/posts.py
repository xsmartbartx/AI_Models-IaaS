from uuid import UUID
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.post import Post
from app.models.character import Character
from app.schemas.post import (
    PostCreate,
    PostUpdate,
    PostResponse,
    PostListResponse,
    GenerateCaptionRequest,
    GenerateCaptionResponse,
    SchedulePostRequest,
    ApprovePostRequest,
)
from app.services.ollama_service import ollama_service
from app.tasks.generation_tasks import publish_content_task

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=PostListResponse)
async def list_posts(
    character_id: Optional[UUID] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    platform: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List posts, optionally filtered by character, status, or platform."""
    query = select(Post).order_by(Post.created_at.desc())

    if character_id:
        query = query.filter(Post.character_id == character_id)
    if status_filter:
        query = query.filter(Post.status == status_filter)
    if platform:
        query = query.filter(Post.platform == platform)

    result = await db.execute(query)
    posts = result.scalars().all()
    return PostListResponse(
        items=[PostResponse.model_validate(p) for p in posts],
        total=len(posts),
    )


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(data: PostCreate, db: AsyncSession = Depends(get_db)):
    """Create a new post."""
    # Validate character exists
    result = await db.execute(select(Character).filter(Character.id == data.character_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Character not found")

    post = Post(
        character_id=data.character_id,
        platform=data.platform,
        caption=data.caption,
        hashtags=data.hashtags,
        media_ids=data.media_ids,
        publish_date=data.publish_date,
        status="draft",
    )
    db.add(post)
    await db.flush()
    await db.refresh(post)
    return PostResponse.model_validate(post)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single post by ID."""
    result = await db.execute(select(Post).filter(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostResponse.model_validate(post)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(post_id: UUID, data: PostUpdate, db: AsyncSession = Depends(get_db)):
    """Update a post."""
    result = await db.execute(select(Post).filter(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(post, key, value)

    await db.flush()
    await db.refresh(post)
    return PostResponse.model_validate(post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a post."""
    result = await db.execute(select(Post).filter(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    await db.delete(post)
    await db.flush()


@router.post("/generate-caption", response_model=GenerateCaptionResponse)
async def generate_caption(data: GenerateCaptionRequest, db: AsyncSession = Depends(get_db)):
    """Generate a caption and hashtags using Ollama LLM."""
    result = await db.execute(select(Character).filter(Character.id == data.character_id))
    char = result.scalar_one_or_none()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")

    generated = await ollama_service.generate_caption(
        character_name=char.name,
        character_bio=char.bio or "",
        topic=data.topic or "",
        tone=data.tone or "casual",
        language=data.language or "english",
    )

    return GenerateCaptionResponse(
        caption=generated["caption"],
        hashtags=generated.get("hashtags", []),
    )


@router.post("/{post_id}/approve", response_model=PostResponse)
async def approve_post(post_id: UUID, data: ApprovePostRequest, db: AsyncSession = Depends(get_db)):
    """Approve a post for publishing."""
    result = await db.execute(select(Post).filter(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.status = "approved"
    post.approved_by = data.approved_by or "admin"
    post.approved_at = datetime.utcnow()

    await db.flush()
    await db.refresh(post)
    return PostResponse.model_validate(post)


@router.post("/{post_id}/reject", response_model=PostResponse)
async def reject_post(post_id: UUID, db: AsyncSession = Depends(get_db)):
    """Reject a post - send back to draft."""
    result = await db.execute(select(Post).filter(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.status = "rejected"
    await db.flush()
    await db.refresh(post)
    return PostResponse.model_validate(post)


@router.post("/{post_id}/publish", status_code=status.HTTP_202_ACCEPTED)
async def publish_post(post_id: UUID, db: AsyncSession = Depends(get_db)):
    """Queue a post for publishing."""
    result = await db.execute(select(Post).filter(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.status != "approved":
        raise HTTPException(status_code=400, detail="Only approved posts can be published")

    task = publish_content_task.delay(str(post_id))
    return {"status": "processing", "task_id": task.id, "message": "Post publishing queued"}


@router.post("/{post_id}/schedule", response_model=PostResponse)
async def schedule_post(post_id: UUID, data: SchedulePostRequest, db: AsyncSession = Depends(get_db)):
    """Schedule a post for a specific date/time."""
    result = await db.execute(select(Post).filter(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.publish_date = data.publish_date
    post.status = "scheduled"

    await db.flush()
    await db.refresh(post)
    return PostResponse.model_validate(post)
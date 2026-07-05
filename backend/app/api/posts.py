from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.post import Post
from backend.app.schemas.post import (
    PostCreate,
    PostUpdate,
    PostResponse,
    PostListResponse,
    GenerateCaptionRequest,
    GenerateCaptionResponse,
)
from backend.app.services.ollama_service import ollama_service
from backend.app.models.character import Character

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=PostListResponse)
def list_posts(character_id: UUID = None, status_filter: str = None, db: Session = Depends(get_db)):
    """List posts, optionally filtered by character or status."""
    query = db.query(Post).order_by(Post.created_at.desc())
    if character_id:
        query = query.filter(Post.character_id == character_id)
    if status_filter:
        query = query.filter(Post.status == status_filter)
    posts = query.all()
    return PostListResponse(
        items=[PostResponse.model_validate(p) for p in posts],
        total=len(posts),
    )


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(data: PostCreate, db: Session = Depends(get_db)):
    """Create a new post."""
    post = Post(
        character_id=data.character_id,
        platform=data.platform,
        caption=data.caption,
        hashtags=data.hashtags,
        media_ids=data.media_ids,
        publish_date=data.publish_date,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return PostResponse.model_validate(post)


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: UUID, db: Session = Depends(get_db)):
    """Get a single post by ID."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostResponse.model_validate(post)


@router.patch("/{post_id}", response_model=PostResponse)
def update_post(post_id: UUID, data: PostUpdate, db: Session = Depends(get_db)):
    """Update a post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(post, key, value)

    db.commit()
    db.refresh(post)
    return PostResponse.model_validate(post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: UUID, db: Session = Depends(get_db)):
    """Delete a post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()


@router.post("/generate-caption", response_model=GenerateCaptionResponse)
async def generate_caption(data: GenerateCaptionRequest, db: Session = Depends(get_db)):
    """Generate a caption and hashtags using Ollama LLM."""
    char = db.query(Character).filter(Character.id == data.character_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")

    result = await ollama_service.generate_caption(
        character_name=char.name,
        character_bio=char.bio or "",
        topic=data.topic or "",
        tone=data.tone,
        language=data.language,
    )

    return GenerateCaptionResponse(
        caption=result["caption"],
        hashtags=result["hashtags"],
    )
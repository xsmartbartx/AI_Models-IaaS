from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class PostCreate(BaseModel):
    character_id: UUID
    platform: str
    caption: Optional[str] = None
    hashtags: Optional[str] = None
    media_ids: Optional[str] = None
    publish_date: Optional[datetime] = None


class PostUpdate(BaseModel):
    caption: Optional[str] = None
    hashtags: Optional[str] = None
    status: Optional[str] = None
    publish_date: Optional[datetime] = None


class PostResponse(BaseModel):
    id: UUID
    character_id: UUID
    platform: str
    caption: Optional[str] = None
    hashtags: Optional[str] = None
    media_ids: Optional[str] = None
    status: str
    publish_date: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    items: list[PostResponse]
    total: int


class GenerateCaptionRequest(BaseModel):
    character_id: UUID
    topic: Optional[str] = None
    tone: str = "casual"
    language: str = "english"


class GenerateCaptionResponse(BaseModel):
    caption: str
    hashtags: list[str]
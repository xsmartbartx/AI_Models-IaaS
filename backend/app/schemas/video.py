from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class VideoGenerateRequest(BaseModel):
    character_id: UUID
    source_image_id: Optional[UUID] = None
    prompt: Optional[str] = None


class VideoResponse(BaseModel):
    id: UUID
    character_id: UUID
    source_image_id: Optional[UUID] = None
    file_path: str
    thumbnail_path: Optional[str] = None
    duration: Optional[float] = None
    prompt: Optional[str] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class VideoListResponse(BaseModel):
    items: list[VideoResponse]
    total: int
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class ImageGenerateRequest(BaseModel):
    character_id: UUID
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    category: str = "general"
    count: int = 1


class ImageResponse(BaseModel):
    id: UUID
    character_id: UUID
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    file_path: str
    thumbnail_path: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    category: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ImageListResponse(BaseModel):
    items: list[ImageResponse]
    total: int
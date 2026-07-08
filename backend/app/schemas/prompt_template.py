from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PromptTemplateCreate(BaseModel):
    """Schema for creating a prompt template."""
    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    category: str = Field(default="general", description="Category: lifestyle, gym, travel, fashion, etc")
    template_type: str = Field(default="image", description="Type: image, video, caption")
    prompt: str = Field(..., description="The prompt text")
    negative_prompt: Optional[str] = Field(None, description="Negative prompt for image generation")
    icon: Optional[str] = Field(None, description="Emoji or icon identifier")


class PromptTemplateUpdate(BaseModel):
    """Schema for updating a prompt template (partial)."""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    template_type: Optional[str] = None
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    icon: Optional[str] = None


class PromptTemplateResponse(BaseModel):
    """Schema for prompt template API response."""
    id: UUID
    name: str
    description: Optional[str] = None
    category: str
    template_type: str
    prompt: str
    negative_prompt: Optional[str] = None
    icon: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PromptTemplateListResponse(BaseModel):
    """Schema for list of prompt templates."""
    items: list[PromptTemplateResponse]
    total: int
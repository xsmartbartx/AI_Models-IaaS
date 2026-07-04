from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class AppearanceSchema(BaseModel):
    hair: str = ""
    eyes: str = ""
    skin_tone: str = ""
    face_shape: str = ""
    body_type: str = ""


class CharacterCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=18, le=45)
    nationality: str = Field(..., min_length=1, max_length=100)
    hair: str = Field(..., min_length=1, max_length=50)
    eyes: str = Field(..., min_length=1, max_length=50)
    height: str = Field(..., min_length=1, max_length=10)
    style: str = Field(..., min_length=1, max_length=100)
    bio: Optional[str] = None
    appearance: Optional[AppearanceSchema] = None
    hobbies: Optional[list[str]] = []


class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    nationality: Optional[str] = None
    hair: Optional[str] = None
    eyes: Optional[str] = None
    height: Optional[str] = None
    style: Optional[str] = None
    bio: Optional[str] = None
    appearance: Optional[dict] = None
    hobbies: Optional[list[str]] = None
    status: Optional[str] = None


class CharacterResponse(BaseModel):
    id: UUID
    name: str
    age: int
    nationality: str
    hair: str
    eyes: str
    height: str
    style: str
    bio: Optional[str] = None
    appearance: Optional[dict] = None
    hobbies: Optional[list] = None
    reference_image_path: Optional[str] = None
    instantid_model_path: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CharacterListResponse(BaseModel):
    items: list[CharacterResponse]
    total: int
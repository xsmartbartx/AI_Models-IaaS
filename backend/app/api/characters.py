from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.character import Character
from app.schemas.character import (
    CharacterCreate,
    CharacterUpdate,
    CharacterResponse,
    CharacterListResponse,
)

router = APIRouter(prefix="/characters", tags=["characters"])


@router.get("/", response_model=CharacterListResponse)
async def list_characters(db: AsyncSession = Depends(get_db)):
    """List all characters."""
    result = await db.execute(select(Character).order_by(Character.created_at.desc()))
    characters = result.scalars().all()
    return CharacterListResponse(
        items=[CharacterResponse.model_validate(c) for c in characters],
        total=len(characters),
    )


@router.post("/", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character(data: CharacterCreate, db: AsyncSession = Depends(get_db)):
    """Create a new AI character."""
    char = Character(
        name=data.name,
        age=data.age,
        nationality=data.nationality,
        hair=data.hair,
        eyes=data.eyes,
        height=data.height,
        style=data.style,
        bio=data.bio,
        appearance=data.appearance.model_dump() if data.appearance else {},
        hobbies=data.hobbies,
    )
    db.add(char)
    await db.flush()
    await db.refresh(char)
    return CharacterResponse.model_validate(char)


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(character_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single character by ID."""
    result = await db.execute(select(Character).filter(Character.id == character_id))
    char = result.scalar_one_or_none()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    return CharacterResponse.model_validate(char)


@router.patch("/{character_id}", response_model=CharacterResponse)
async def update_character(character_id: UUID, data: CharacterUpdate, db: AsyncSession = Depends(get_db)):
    """Update a character."""
    result = await db.execute(select(Character).filter(Character.id == character_id))
    char = result.scalar_one_or_none()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(char, key, value)

    await db.flush()
    await db.refresh(char)
    return CharacterResponse.model_validate(char)


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(character_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a character."""
    result = await db.execute(select(Character).filter(Character.id == character_id))
    char = result.scalar_one_or_none()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    await db.delete(char)
    await db.flush()


@router.post("/{character_id}/activate", response_model=CharacterResponse)
async def activate_character(character_id: UUID, db: AsyncSession = Depends(get_db)):
    """Activate a character for content generation."""
    result = await db.execute(select(Character).filter(Character.id == character_id))
    char = result.scalar_one_or_none()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    char.status = "active"
    await db.flush()
    await db.refresh(char)
    return CharacterResponse.model_validate(char)
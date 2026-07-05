from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.character import Character
from backend.app.schemas.character import (
    CharacterCreate,
    CharacterUpdate,
    CharacterResponse,
    CharacterListResponse,
)
from backend.app.tasks.generation_tasks import generate_caption_task

router = APIRouter(prefix="/characters", tags=["characters"])


@router.get("/", response_model=CharacterListResponse)
def list_characters(db: Session = Depends(get_db)):
    """List all characters."""
    characters = db.query(Character).order_by(Character.created_at.desc()).all()
    return CharacterListResponse(
        items=[CharacterResponse.model_validate(c) for c in characters],
        total=len(characters),
    )


@router.post("/", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
def create_character(data: CharacterCreate, db: Session = Depends(get_db)):
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
    db.commit()
    db.refresh(char)
    return CharacterResponse.model_validate(char)


@router.get("/{character_id}", response_model=CharacterResponse)
def get_character(character_id: UUID, db: Session = Depends(get_db)):
    """Get a single character by ID."""
    char = db.query(Character).filter(Character.id == character_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    return CharacterResponse.model_validate(char)


@router.patch("/{character_id}", response_model=CharacterResponse)
def update_character(character_id: UUID, data: CharacterUpdate, db: Session = Depends(get_db)):
    """Update a character."""
    char = db.query(Character).filter(Character.id == character_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(char, key, value)

    db.commit()
    db.refresh(char)
    return CharacterResponse.model_validate(char)


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_character(character_id: UUID, db: Session = Depends(get_db)):
    """Delete a character."""
    char = db.query(Character).filter(Character.id == character_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    db.delete(char)
    db.commit()


@router.post("/{character_id}/activate", response_model=CharacterResponse)
def activate_character(character_id: UUID, db: Session = Depends(get_db)):
    """Activate a character for content generation."""
    char = db.query(Character).filter(Character.id == character_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    char.status = "active"
    db.commit()
    db.refresh(char)
    return CharacterResponse.model_validate(char)
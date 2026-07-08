from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models.prompt_template import PromptTemplate
from backend.app.schemas.prompt_template import (
    PromptTemplateCreate,
    PromptTemplateUpdate,
    PromptTemplateResponse,
    PromptTemplateListResponse,
)

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.get("/", response_model=PromptTemplateListResponse)
async def list_templates(
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all prompt templates, optionally filtered by category."""
    query = select(PromptTemplate).order_by(PromptTemplate.created_at.desc())
    if category:
        query = query.filter(PromptTemplate.category == category)
    result = await db.execute(query)
    templates = result.scalars().all()
    return PromptTemplateListResponse(
        items=[PromptTemplateResponse.model_validate(t) for t in templates],
        total=len(templates),
    )


@router.post("/", response_model=PromptTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(data: PromptTemplateCreate, db: AsyncSession = Depends(get_db)):
    """Create a new prompt template."""
    template = PromptTemplate(
        name=data.name,
        description=data.description,
        category=data.category,
        template_type=data.template_type,
        prompt=data.prompt,
        negative_prompt=data.negative_prompt,
        icon=data.icon,
    )
    db.add(template)
    await db.flush()
    await db.refresh(template)
    return PromptTemplateResponse.model_validate(template)


@router.get("/{template_id}", response_model=PromptTemplateResponse)
async def get_template(template_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single prompt template by ID."""
    result = await db.execute(select(PromptTemplate).filter(PromptTemplate.id == template_id))
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return PromptTemplateResponse.model_validate(template)


@router.patch("/{template_id}", response_model=PromptTemplateResponse)
async def update_template(template_id: UUID, data: PromptTemplateUpdate, db: AsyncSession = Depends(get_db)):
    """Update a prompt template."""
    result = await db.execute(select(PromptTemplate).filter(PromptTemplate.id == template_id))
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Prompt template not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(template, key, value)

    await db.flush()
    await db.refresh(template)
    return PromptTemplateResponse.model_validate(template)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(template_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a prompt template."""
    result = await db.execute(select(PromptTemplate).filter(PromptTemplate.id == template_id))
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    await db.delete(template)
    await db.flush()
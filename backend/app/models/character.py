import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    nationality: Mapped[str] = mapped_column(String(100), nullable=False)
    hair: Mapped[str] = mapped_column(String(50), nullable=False)
    eyes: Mapped[str] = mapped_column(String(50), nullable=False)
    height: Mapped[str] = mapped_column(String(10), nullable=False)
    style: Mapped[str] = mapped_column(String(100), nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    appearance: Mapped[dict] = mapped_column(JSON, nullable=True, default=dict)
    hobbies: Mapped[dict] = mapped_column(JSON, nullable=True, default=list)
    reference_image_path: Mapped[str] = mapped_column(String(500), nullable=True)
    instantid_model_path: Mapped[str] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    images = relationship("Image", back_populates="character", cascade="all, delete-orphan")
    videos = relationship("Video", back_populates="character", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="character", cascade="all, delete-orphan")
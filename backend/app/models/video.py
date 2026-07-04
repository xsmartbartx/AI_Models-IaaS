import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from backend.app.core.database import Base


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("characters.id"), nullable=False)
    source_image_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("images.id"), nullable=True)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_path: Mapped[str] = mapped_column(String(500), nullable=True)
    duration: Mapped[float] = mapped_column(Float, nullable=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="generated")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    character = relationship("Character", back_populates="videos")
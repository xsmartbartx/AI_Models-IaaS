import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("characters.id"), nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    caption: Mapped[str] = mapped_column(Text, nullable=True)
    hashtags: Mapped[str] = mapped_column(Text, nullable=True)
    media_ids: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    publish_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    approved_by: Mapped[str] = mapped_column(String(255), nullable=True)
    approved_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    character = relationship("Character", back_populates="posts")
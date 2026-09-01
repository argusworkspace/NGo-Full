import uuid
import datetime
from sqlalchemy import String, Enum as SAEnum, ForeignKey, DateTime, func, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (Index("ix_projects_created_by", "created_by"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    questions: Mapped[list] = mapped_column(JSONB, default=list)
    status: Mapped[str] = mapped_column(
        SAEnum("DRAFT", "PUBLISHED", "ARCHIVED", name="project_status"), default="DRAFT"
    )
    created_by: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Response(Base):
    __tablename__ = "responses"
    __table_args__ = (
        Index("ix_responses_project_id", "project_id"),
        Index("ix_responses_user_id", "user_id"),
        Index("ix_responses_submitted_at", "submitted_at"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String, ForeignKey("projects.id", ondelete="CASCADE"))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    answers: Mapped[list] = mapped_column(JSONB, default=list)
    submitted_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

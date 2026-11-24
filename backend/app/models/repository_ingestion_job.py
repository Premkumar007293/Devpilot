"""RepositoryIngestionJob database model tracking ingestion lifecycle and stats."""

import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.repository import Repository


class IngestionStatus(str, enum.Enum):
    """Lifecycle states of repository ingestion pipeline."""
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RepositoryIngestionJob(Base):
    """Ingestion job tracking git tree synchronization, progress, and file counts."""

    __tablename__ = "repository_ingestion_jobs"

    __table_args__ = (
        Index("ix_ingestion_jobs_repo_status", "repository_id", "status"),
        Index("ix_ingestion_jobs_status_created", "status", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    repository_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default=IngestionStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    branch: Mapped[str] = mapped_column(
        String(128),
        default="main",
        nullable=False,
    )
    commit_sha: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )
    total_files: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    source_files: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    ignored_files: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    total_bytes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    progress: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationship
    repository: Mapped["Repository"] = relationship(
        "Repository",
        back_populates="ingestion_jobs",
    )


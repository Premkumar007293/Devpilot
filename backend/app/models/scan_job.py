"""ScanJob database model."""

import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.repository import Repository


class ScanJobStatus(str, enum.Enum):
    """Scan job execution lifecycle states."""
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ScanType(str, enum.Enum):
    """Scan intelligence target types."""
    FULL = "full"
    SECURITY = "security"
    AST = "ast"
    COMPLEXITY = "complexity"


class ScanJob(Base):
    """Scan job model tracking code intelligence analysis lifecycle and metrics."""

    __tablename__ = "scan_jobs"

    __table_args__ = (
        Index("ix_scan_jobs_repo_status", "repository_id", "status"),
        Index("ix_scan_jobs_status_created", "status", "created_at"),
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
        default=ScanJobStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    scan_type: Mapped[str] = mapped_column(
        String(64),
        default=ScanType.FULL.value,
        nullable=False,
        index=True,
    )
    progress: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    repository: Mapped["Repository"] = relationship(
        "Repository",
        back_populates="scan_jobs",
    )

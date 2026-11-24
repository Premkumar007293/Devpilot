"""RepositoryFile database model for ingested codebases."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.repository import Repository


class RepositoryFile(Base):
    """File metadata and source preview storage for ingested repositories."""

    __tablename__ = "repository_files"

    __table_args__ = (
        UniqueConstraint("repository_id", "path", name="uq_repo_file_path"),
        Index("ix_repository_files_repo_type", "repository_id", "file_type"),
        Index("ix_repository_files_repo_ext", "repository_id", "extension"),
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
    path: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    extension: Mapped[str] = mapped_column(
        String(64),
        default="",
        nullable=False,
    )
    size_bytes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    file_type: Mapped[str] = mapped_column(
        String(32),
        default="source",
        nullable=False,
    )  # source, config, doc, asset
    blob_sha: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )
    branch: Mapped[str] = mapped_column(
        String(128),
        default="main",
        nullable=False,
    )
    content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    is_binary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    last_ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship
    repository: Mapped["Repository"] = relationship(
        "Repository",
        back_populates="files",
    )


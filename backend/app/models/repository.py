"""Repository database model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.scan_job import ScanJob
    from app.models.repository_file import RepositoryFile
    from app.models.repository_ingestion_job import RepositoryIngestionJob
    from app.models.user import User
    from app.models.architecture_snapshot import ArchitectureSnapshot


class Repository(Base, TimestampMixin):
    """Repository entity tracking monitored VCS codebases and scan histories."""

    __tablename__ = "repositories"

    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uq_org_repo_name"),
        Index("ix_repositories_org_active", "organization_id", "is_active"),
        Index("ix_repositories_provider_ext", "provider", "external_id"),
        Index("ix_repositories_owner", "owner_user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    owner_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        default="",
    )
    provider: Mapped[str] = mapped_column(
        String(64),
        default="github",
        nullable=False,
        index=True,
    )
    external_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    html_url: Mapped[Optional[str]] = mapped_column(
        String(1024),
        nullable=True,
    )
    default_branch: Mapped[str] = mapped_column(
        String(128),
        default="main",
        nullable=False,
    )
    is_private: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    language: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )
    stars_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    last_scanned_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_ingested_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    ingestion_status: Mapped[str] = mapped_column(
        String(32),
        default="NOT_INGESTED",
        nullable=False,
    )
    file_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    source_file_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="repositories",
    )
    owner_user: Mapped[Optional["User"]] = relationship(
        "User",
    )
    scan_jobs: Mapped[List["ScanJob"]] = relationship(
        "ScanJob",
        back_populates="repository",
        cascade="all, delete-orphan",
    )
    files: Mapped[List["RepositoryFile"]] = relationship(
        "RepositoryFile",
        back_populates="repository",
        cascade="all, delete-orphan",
    )
    ingestion_jobs: Mapped[List["RepositoryIngestionJob"]] = relationship(
        "RepositoryIngestionJob",
        back_populates="repository",
        cascade="all, delete-orphan",
    )
    architecture_snapshots: Mapped[List["ArchitectureSnapshot"]] = relationship(
        "ArchitectureSnapshot",
        back_populates="repository",
        cascade="all, delete-orphan",
    )

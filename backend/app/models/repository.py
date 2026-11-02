"""Repository database model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.scan_job import ScanJob


class Repository(Base, TimestampMixin):
    """Repository entity tracking monitored VCS codebases and scan histories."""

    __tablename__ = "repositories"

    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uq_org_repo_name"),
        Index("ix_repositories_org_active", "organization_id", "is_active"),
        Index("ix_repositories_provider_ext", "provider", "external_id"),
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
    last_scanned_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="repositories",
    )
    scan_jobs: Mapped[List["ScanJob"]] = relationship(
        "ScanJob",
        back_populates="repository",
        cascade="all, delete-orphan",
    )

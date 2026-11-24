"""User-facing notification model for DevPilot events."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.repository import Repository
    from app.models.user import User


class Notification(Base, TimestampMixin):
    """Persistent notification entry for repository or system events."""

    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    repository_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        ForeignKey("repositories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )
    notification_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="info",
        index=True,
    )
    severity: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="info",
        index=True,
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )
    related_resource_type: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )
    related_resource_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    user: Mapped["User"] = relationship("User")
    organization: Mapped[Optional["Organization"]] = relationship("Organization")
    repository: Mapped[Optional["Repository"]] = relationship("Repository")

"""Feedback model for beta user reports and issue tracking."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.repository import Repository
    from app.models.user import User


class Feedback(Base, TimestampMixin):
    """User-submitted feedback, bug reports, and usability notes."""

    __tablename__ = "feedback"

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
    repository_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        ForeignKey("repositories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    category: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="general",
        index=True,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    related_resource_type: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )
    related_resource_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="new",
        index=True,
    )

    user: Mapped["User"] = relationship("User")
    repository: Mapped[Optional["Repository"]] = relationship("Repository")

"""Organization database model."""

import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.organization_member import OrganizationMember
    from app.models.repository import Repository


class Organization(Base, TimestampMixin):
    """Organization entity grouping repositories, teams, and access control."""

    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        default="",
    )

    # Relationships
    members: Mapped[List["OrganizationMember"]] = relationship(
        "OrganizationMember",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    repositories: Mapped[List["Repository"]] = relationship(
        "Repository",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

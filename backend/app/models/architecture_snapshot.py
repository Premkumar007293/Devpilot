"""Stored analysis snapshots for repository architecture graphs."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.repository import Repository


class ArchitectureSnapshot(Base, TimestampMixin):
    """Serializable snapshot of a repository architecture analysis."""

    __tablename__ = "architecture_snapshots"

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
        default="pending",
        nullable=False,
    )
    analysis_version: Mapped[str] = mapped_column(
        String(64),
        default="architecture-v1",
        nullable=False,
    )
    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    node_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    edge_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    cycle_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    nodes_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    edges_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    cycles_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    layers_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    entrypoints_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    repository: Mapped["Repository"] = relationship(
        "Repository",
        back_populates="architecture_snapshots",
    )

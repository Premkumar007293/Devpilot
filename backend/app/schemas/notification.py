"""Notification API schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NotificationBase(BaseModel):
    title: str = Field(..., max_length=255)
    message: str
    notification_type: str = Field(default="info", max_length=64)
    severity: str = Field(default="info", max_length=32)
    organization_id: uuid.UUID | None = None
    repository_id: uuid.UUID | None = None
    related_resource_type: str | None = None
    related_resource_id: str | None = None


class NotificationCreate(NotificationBase):
    """Schema used to create a notification record."""


class NotificationResponse(NotificationBase):
    id: uuid.UUID
    user_id: uuid.UUID
    is_read: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationCountResponse(BaseModel):
    count: int

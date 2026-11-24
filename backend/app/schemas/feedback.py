"""Feedback request and response schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FeedbackCreate(BaseModel):
    category: str = Field(default="general", max_length=64)
    description: str = Field(..., min_length=1, max_length=5000)
    repository_id: uuid.UUID | None = None
    related_resource_type: str | None = None
    related_resource_id: str | None = None


class FeedbackResponse(FeedbackCreate):
    id: uuid.UUID
    user_id: uuid.UUID
    status: str = "new"
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

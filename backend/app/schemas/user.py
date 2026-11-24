"""User Pydantic schemas."""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user fields."""

    email: EmailStr = Field(..., description="User primary email address", json_schema_extra={"example": "developer@devpilot.ai"})
    username: str = Field(..., min_length=2, max_length=100, description="Unique account username", json_schema_extra={"example": "lead_dev"})
    full_name: Optional[str] = Field("", max_length=255, description="Full display name", json_schema_extra={"example": "Lead Developer"})
    avatar_url: Optional[str] = Field(None, max_length=1024, description="Profile avatar URL")


class UserCreate(UserBase):
    """Schema for registering a new user."""
    pass


class UserResponse(UserBase):
    """Public user response schema."""

    id: uuid.UUID
    github_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

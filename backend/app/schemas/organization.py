"""Organization and membership Pydantic schemas."""

import re
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.organization_member import MemberRole
from app.schemas.user import UserResponse


def generate_slug(text: str) -> str:
    """Transform string into a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


class OrganizationBase(BaseModel):
    """Base organization fields."""

    name: str = Field(..., min_length=2, max_length=255, description="Organization display name", json_schema_extra={"example": "Acme Engineering"})
    slug: Optional[str] = Field(None, min_length=2, max_length=255, description="Unique URL slug (generated if omitted)", json_schema_extra={"example": "acme-engineering"})
    description: Optional[str] = Field(None, description="Detailed organization description", json_schema_extra={"example": "Core engineering team"})

    @field_validator("slug", mode="before")
    @classmethod
    def sanitize_slug(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return generate_slug(v)
        return v


class OrganizationCreate(OrganizationBase):
    """Schema for creating a new organization."""
    pass


class OrganizationUpdate(BaseModel):
    """Schema for updating organization attributes."""

    name: Optional[str] = Field(None, min_length=2, max_length=255)
    slug: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None

    @field_validator("slug", mode="before")
    @classmethod
    def sanitize_slug(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return generate_slug(v)
        return v


class OrganizationResponse(BaseModel):
    """Organization serialized response."""

    id: uuid.UUID
    name: str
    slug: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    member_count: Optional[int] = 0
    repository_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class OrganizationMemberCreate(BaseModel):
    """Schema for adding a member to an organization."""

    user_id: uuid.UUID
    role: MemberRole = Field(default=MemberRole.MEMBER, description="Member role (OWNER, ADMIN, MEMBER)")


class OrganizationMemberResponse(BaseModel):
    """Organization membership response."""

    id: uuid.UUID
    user_id: uuid.UUID
    organization_id: uuid.UUID
    role: str
    joined_at: datetime
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)

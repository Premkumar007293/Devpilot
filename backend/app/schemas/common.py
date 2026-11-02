"""Common response and pagination schemas."""

from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class RootResponse(BaseModel):
    """API root response schema matching specifications."""

    message: str = Field(..., description="Welcome greeting message", json_schema_extra={"example": "Welcome to DevPilot API"})
    version: str = Field(..., description="API version", json_schema_extra={"example": "1.0.0"})


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


class PaginationParams(BaseModel):
    """Standard pagination query parameters."""

    skip: int = Field(0, ge=0, description="Records to skip for pagination")
    limit: int = Field(20, ge=1, le=100, description="Max records to return per page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic wrapper for paginated collections."""

    items: List[T]
    total: int
    skip: int
    limit: int

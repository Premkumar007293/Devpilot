"""Common response schemas."""

from pydantic import BaseModel, Field


class RootResponse(BaseModel):
    """API root response schema matching specifications."""

    message: str = Field(..., description="Welcome greeting message", json_schema_extra={"example": "Welcome to DevPilot API"})
    version: str = Field(..., description="API version", json_schema_extra={"example": "1.0.0"})


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str

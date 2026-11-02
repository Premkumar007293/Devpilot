"""Schemas for health check and system diagnostic endpoints."""

from typing import Dict, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response schema exactly matching specifications."""

    status: str = Field(..., description="Application health status", json_schema_extra={"example": "healthy"})
    application: str = Field(..., description="Application name", json_schema_extra={"example": "DevPilot"})
    version: str = Field(..., description="Application version", json_schema_extra={"example": "1.0.0"})


class SystemDiagnosticsResponse(BaseModel):
    """Detailed system diagnostic status schema for Phase 1 infrastructure verification."""

    status: str
    application: str
    version: str
    environment: str
    database: Dict[str, Any]
    redis: Dict[str, Any]
    ai_providers: Dict[str, Any]

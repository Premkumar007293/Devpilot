"""Health check endpoints for monitoring and orchestrator liveness checks."""

from fastapi import APIRouter, status
from app.schemas.health import HealthResponse, SystemDiagnosticsResponse
from app.services.health_service import HealthService

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Application Health Status",
    description="Returns standard liveness and basic application health status.",
)
async def get_health() -> HealthResponse:
    """Return application health status."""
    return HealthResponse(**HealthService.get_basic_health())


@router.get(
    "/health/diagnostics",
    response_model=SystemDiagnosticsResponse,
    status_code=status.HTTP_200_OK,
    summary="System Diagnostic Checks",
    description="Performs deep connectivity verification on PostgreSQL, Redis, and AI providers.",
)
async def get_health_diagnostics() -> SystemDiagnosticsResponse:
    """Return detailed system diagnostic status."""
    return SystemDiagnosticsResponse(**HealthService.get_system_diagnostics())

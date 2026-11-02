"""API v1 root welcome endpoint."""

from fastapi import APIRouter, status
from app.core.config import settings
from app.schemas.common import RootResponse

router = APIRouter()


@router.get(
    "/",
    response_model=RootResponse,
    status_code=status.HTTP_200_OK,
    summary="API Root Information",
    description="Returns welcome message and API version indicator.",
)
async def get_api_root() -> RootResponse:
    """Return welcome message and version."""
    return RootResponse(
        message="Welcome to DevPilot API",
        version=settings.APP_VERSION,
    )

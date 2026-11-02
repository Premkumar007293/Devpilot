"""Central API v1 router consolidating all endpoint modules."""

from fastapi import APIRouter
from app.api.v1.endpoints import health, organizations, repositories, root, scans

api_router = APIRouter()

# Root & Health endpoints
api_router.include_router(root.router, tags=["API Root"])
api_router.include_router(health.router, tags=["Health & Diagnostics"])

# Phase 2 Core Intelligence Endpoints
api_router.include_router(
    organizations.router,
    prefix="/organizations",
    tags=["Organizations"],
)
api_router.include_router(
    repositories.router,
    prefix="/repositories",
    tags=["Repositories"],
)
api_router.include_router(
    scans.router,
    prefix="/scans",
    tags=["Scan Jobs"],
)

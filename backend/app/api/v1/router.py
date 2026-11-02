"""Central API v1 router consolidating all endpoint modules."""

from fastapi import APIRouter
from app.api.v1.endpoints import health, root

api_router = APIRouter()

# Include root endpoints: GET /api/v1/
api_router.include_router(root.router, tags=["API Root"])

# Include health endpoints: GET /api/v1/health
api_router.include_router(health.router, tags=["Health & Diagnostics"])

"""Central API v1 router consolidating all endpoint modules."""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, feedback, github, health, notifications, organizations, rag, repositories, root, scans, search

api_router = APIRouter()

# Root & Health endpoints
api_router.include_router(root.router, tags=["API Root"])
api_router.include_router(health.router, tags=["Health & Diagnostics"])

# Authentication & GitHub integration
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)
api_router.include_router(
    github.router,
    prefix="/github",
    tags=["GitHub Integration"],
)

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
    rag.router,
    prefix="/rag",
    tags=["Repository RAG"],
)
api_router.include_router(
    scans.router,
    prefix="/scans",
    tags=["Scan Jobs"],
)
api_router.include_router(
    feedback.router,
    prefix="/feedback",
    tags=["Beta Feedback"],
)
api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications"],
)
api_router.include_router(
    search.router,
    prefix="/search",
    tags=["Global Search"],
)

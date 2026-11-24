"""DevPilot Backend Application Entry Point.

FastAPI application initialization with CORS, centralized exception handlers,
and versioned API routing.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.v1.router import api_router
from app.core.callback_bridge import start_callback_bridge, stop_callback_bridge
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown hooks."""
    logger.info("Initializing %s v%s in %s environment...", settings.APP_NAME, settings.APP_VERSION, settings.ENVIRONMENT)
    logger.info("Configured CORS Origins: %s", settings.CORS_ORIGINS)
    start_callback_bridge()
    yield
    stop_callback_bridge()
    logger.info("Shutting down %s...", settings.APP_NAME)


def create_application() -> FastAPI:
    """Factory creating and configuring the FastAPI instance."""
    application = FastAPI(
        title=f"{settings.APP_NAME} API",
        description="Production-oriented AI-powered software development and code intelligence platform API.",
        version=settings.APP_VERSION,
        openapi_url="/api/v1/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Configure Cross-Origin Resource Sharing (CORS)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):\d+",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register centralized exception handlers
    register_exception_handlers(application)

    # Mount versioned API router at /api/v1
    application.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # Root redirect to interactive Swagger documentation
    @application.get("/", include_in_schema=False)
    async def root_redirect():
        return RedirectResponse(url="/docs")

    return application


app = create_application()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
    )

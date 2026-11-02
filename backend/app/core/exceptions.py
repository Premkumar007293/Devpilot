"""Centralized exception handling for DevPilot."""

from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.logging import logger


class DevPilotException(Exception):
    """Base exception for all DevPilot application errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ResourceNotFoundException(DevPilotException):
    """Raised when an entity or resource is not found."""

    def __init__(self, resource_name: str, identifier: Any):
        super().__init__(
            message=f"{resource_name} with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource_name, "identifier": str(identifier)},
        )


class DatabaseConnectionException(DevPilotException):
    """Raised when database connectivity fails."""

    def __init__(self, message: str = "Database connection unavailable"):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class AIProviderException(DevPilotException):
    """Raised when an AI provider call fails or is unconfigured."""

    def __init__(self, provider: str, message: str):
        super().__init__(
            message=f"AI Provider ({provider}) error: {message}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details={"provider": provider},
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Register application-wide exception handlers with FastAPI."""

    @app.exception_handler(DevPilotException)
    async def devpilot_exception_handler(request: Request, exc: DevPilotException):
        logger.error(
            "DevPilot error on %s %s: %s (Status: %d)",
            request.method,
            request.url.path,
            exc.message,
            exc.status_code,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.message,
                "details": exc.details,
                "path": request.url.path,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(
            "Validation error on %s %s: %s",
            request.method,
            request.url.path,
            exc.errors(),
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": True,
                "message": "Input validation failed",
                "details": exc.errors(),
                "path": request.url.path,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception(
            "Unhandled server exception on %s %s: %s",
            request.method,
            request.url.path,
            str(exc),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": True,
                "message": "An internal server error occurred.",
                "path": request.url.path,
            },
        )

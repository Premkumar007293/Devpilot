"""Health check service for application and dependent services."""

from typing import Dict, Any
from app.core.config import settings
from app.database.session import check_database_connection


class HealthService:
    """Service to evaluate application health and dependency statuses."""

    @staticmethod
    def get_basic_health() -> Dict[str, str]:
        """Return standardized basic health response."""
        return {
            "status": "healthy",
            "application": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }

    @staticmethod
    def get_system_diagnostics() -> Dict[str, Any]:
        """Perform non-blocking connectivity checks against database, cache, and providers."""
        db_ok, db_err = check_database_connection()

        # Redis check (safe attempt)
        redis_ok = False
        redis_err = None
        try:
            import redis
            r = redis.from_url(settings.REDIS_URL, socket_timeout=1.0)
            redis_ok = r.ping()
        except Exception as exc:
            redis_err = str(exc)

        return {
            "status": "healthy" if db_ok else "degraded",
            "application": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "database": {
                "connected": db_ok,
                "error": db_err,
                "engine": "PostgreSQL",
            },
            "redis": {
                "connected": redis_ok,
                "error": redis_err,
            },
            "ai_providers": {
                "gemini_configured": bool(settings.GEMINI_API_KEY),
                "openai_configured": bool(settings.OPENAI_API_KEY),
            },
        }

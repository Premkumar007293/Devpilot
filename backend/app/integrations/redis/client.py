"""Redis cache and pub/sub connection client."""

from typing import Any, Optional
import redis
from app.core.config import settings
from app.core.logging import logger


class RedisClient:
    """Wrapper around Redis connection with safe operations and error handling."""

    def __init__(self, url: Optional[str] = None):
        self.url = url or settings.REDIS_URL
        self._client: Optional[redis.Redis] = None

    @property
    def client(self) -> redis.Redis:
        """Lazy initialization of Redis client."""
        if self._client is None:
            self._client = redis.from_url(
                self.url,
                decode_responses=True,
                socket_connect_timeout=2.0,
            )
        return self._client

    def ping(self) -> bool:
        """Check if Redis connection is alive."""
        try:
            return bool(self.client.ping())
        except Exception as exc:
            logger.debug("Redis ping failed: %s", str(exc))
            return False

    def is_available(self) -> bool:
        """Safe non-throwing availability check."""
        return self.ping()

    def get(self, key: str) -> Optional[str]:
        """Safely retrieve value by key."""
        try:
            return self.client.get(key)
        except Exception as exc:
            logger.warning("Redis get failed for key '%s': %s", key, str(exc))
            return None

    def set(self, key: str, value: Any, expire_seconds: Optional[int] = None) -> bool:
        """Safely set key value with optional TTL."""
        try:
            self.client.set(key, str(value), ex=expire_seconds)
            return True
        except Exception as exc:
            logger.warning("Redis set failed for key '%s': %s", key, str(exc))
            return False

    def delete(self, key: str) -> bool:
        """Safely delete key."""
        try:
            self.client.delete(key)
            return True
        except Exception as exc:
            logger.warning("Redis delete failed for key '%s': %s", key, str(exc))
            return False


redis_client = RedisClient()

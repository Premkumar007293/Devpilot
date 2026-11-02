"""Redis cache and pub/sub connection client."""

from typing import Optional
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


redis_client = RedisClient()

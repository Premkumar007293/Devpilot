"""Unit and integration tests for Redis integration and Celery worker tasks."""

from starlette.testclient import TestClient
from app.integrations.redis.client import RedisClient
from app.workers.celery_app import execute_scan_job, get_task_status, ping_worker


def test_celery_ping_task():
    """Verify Celery ping task executes successfully in local/eager mode."""
    result = ping_worker()
    assert result == "pong"


def test_celery_execute_scan_job_task():
    """Verify execute_scan_job task runs with progress tracking."""
    result = execute_scan_job("test-scan-uuid-123")
    assert result["status"] == "COMPLETED"
    assert result["progress"] == 100
    assert result["scan_job_id"] == "test-scan-uuid-123"


def test_celery_get_task_status():
    """Verify get_task_status inspector handles arbitrary task IDs safely."""
    status_info = get_task_status("non-existent-task-id")
    assert isinstance(status_info, dict)
    assert status_info["task_id"] == "non-existent-task-id"


def test_redis_client_safe_degradation():
    """Verify RedisClient methods return gracefully when Redis is unreachable."""
    # Use invalid port to guarantee offline simulation
    offline_client = RedisClient(url="redis://127.0.0.1:59999/0")
    assert offline_client.ping() is False
    assert offline_client.is_available() is False
    assert offline_client.get("test_key") is None
    assert offline_client.set("test_key", "value") is False
    assert offline_client.delete("test_key") is False


def test_health_endpoint_isolation_when_services_offline(client: TestClient):
    """Verify GET /api/v1/health continues reporting healthy even when background cache/db are degraded."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["application"] == "DevPilot"

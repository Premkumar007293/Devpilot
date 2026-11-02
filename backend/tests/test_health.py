"""Tests for API root, health, and Swagger documentation endpoints."""

from starlette.testclient import TestClient


def test_api_v1_health(client: TestClient):
    """Verify GET /api/v1/health returns expected contract."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "status": "healthy",
        "application": "DevPilot",
        "version": "1.0.0",
    }


def test_api_v1_root(client: TestClient):
    """Verify GET /api/v1/ returns expected welcome message."""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "message": "Welcome to DevPilot API",
        "version": "1.0.0",
    }


def test_openapi_docs(client: TestClient):
    """Verify OpenAPI JSON schema is generated and accessible."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "DevPilot API"
    assert schema["info"]["version"] == "1.0.0"
    assert "/api/v1/health" in schema["paths"]
    assert "/api/v1/" in schema["paths"]


def test_cors_headers(client: TestClient):
    """Verify CORS middleware headers are properly returned on preflight requests."""
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"

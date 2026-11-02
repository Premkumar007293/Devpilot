"""Pytest fixtures for backend test suite."""

import pytest
from starlette.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """TestClient fixture for executing API integration tests."""
    with TestClient(app) as test_client:
        yield test_client

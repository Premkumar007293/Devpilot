"""Tests for database foundation and connection verification."""

from app.database.base import Base
from app.database.session import check_database_connection


def test_database_base_metadata():
    """Verify SQLAlchemy Base is initialized and metadata registry is active."""
    assert Base is not None
    assert hasattr(Base, "metadata")


def test_database_connection_checker_safe():
    """Verify check_database_connection executes without throwing uncaught exceptions."""
    is_connected, error = check_database_connection()
    assert isinstance(is_connected, bool)
    if not is_connected:
        assert error is not None

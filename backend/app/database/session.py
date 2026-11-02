"""Database engine creation, session factory, and connection verification."""

from typing import Generator, Tuple, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.logging import logger


def get_engine_args(url: str):
    """Generate engine creation arguments appropriate for the target dialect."""
    if url.startswith("sqlite"):
        return {
            "connect_args": {"check_same_thread": False},
            "echo": False,
        }
    return {
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
        "echo": False,
        "connect_args": {"connect_timeout": 2},
    }


# Create SQLAlchemy engine with pool pre-ping
engine = create_engine(
    settings.DATABASE_URL,
    **get_engine_args(settings.DATABASE_URL),
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency to provide a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> Tuple[bool, Optional[str]]:
    """Test connectivity to database.

    Returns:
        Tuple[bool, Optional[str]]: (is_connected, error_message_if_any)
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, None
    except Exception as exc:
        logger.warning("Database connectivity check failed: %s", str(exc))
        return False, str(exc)

"""Database engine creation, session factory, and connection verification."""

from typing import Generator, Tuple, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.logging import logger

# Create SQLAlchemy engine with pool pre-ping to ensure active connections
# and a fast connect_timeout so offline status is detected promptly
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False,
    connect_args={"connect_timeout": 2},
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
    """Test connectivity to PostgreSQL database.

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

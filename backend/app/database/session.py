"""Database engine creation, session factory, and connection verification."""

from pathlib import Path
from typing import Generator, Tuple, Optional
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.logging import logger


def resolve_database_url(url: str) -> str:
    """Resolve database URL, converting relative SQLite paths to absolute backend paths."""
    if url.startswith("sqlite:///") and not url.startswith("sqlite:////") and ":memory:" not in url:
        rel_path = url[len("sqlite:///"):]
        backend_dir = Path(__file__).resolve().parent.parent.parent
        abs_path = (backend_dir / rel_path).resolve()
        return f"sqlite:///{abs_path.as_posix()}"
    return url


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


# Create SQLAlchemy engine with dialect-appropriate options
resolved_db_url = resolve_database_url(settings.DATABASE_URL)
engine = create_engine(
    resolved_db_url,
    **get_engine_args(resolved_db_url),
)

# Enable foreign key constraint enforcement in SQLite
if resolved_db_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

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

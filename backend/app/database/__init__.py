"""Database module containing session management, connection engines, and declarative base."""

from app.database.base import Base

__all__ = ["Base", "SessionLocal", "engine", "get_db", "check_database_connection"]


def __getattr__(name):
    if name in {"SessionLocal", "engine", "get_db", "check_database_connection"}:
        from app.database.session import SessionLocal, engine, get_db, check_database_connection
        return {
            "SessionLocal": SessionLocal,
            "engine": engine,
            "get_db": get_db,
            "check_database_connection": check_database_connection,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

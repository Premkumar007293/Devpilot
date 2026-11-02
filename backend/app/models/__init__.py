"""Database Models Package.

All domain models will be registered here for Alembic discovery and metadata tracking.
"""

from app.database.base import Base

# Export Base so Alembic env.py can import target_metadata = Base.metadata
__all__ = ["Base"]

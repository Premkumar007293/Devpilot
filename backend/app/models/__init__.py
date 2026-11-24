"""Database Models Package.

All domain models are registered here for Alembic discovery and metadata tracking.
"""

from app.database.base import Base
from app.models.user import User
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember, MemberRole
from app.models.repository import Repository
from app.models.scan_job import ScanJob, ScanJobStatus, ScanType
from app.models.repository_file import RepositoryFile
from app.models.repository_ingestion_job import RepositoryIngestionJob, IngestionStatus
from app.models.architecture_snapshot import ArchitectureSnapshot
from app.models.feedback import Feedback
from app.models.notification import Notification
from app.models.webhook_event import WebhookEvent

__all__ = [
    "Base",
    "User",
    "Organization",
    "OrganizationMember",
    "MemberRole",
    "Repository",
    "ScanJob",
    "ScanJobStatus",
    "ScanType",
    "RepositoryFile",
    "RepositoryIngestionJob",
    "IngestionStatus",
    "ArchitectureSnapshot",
    "Feedback",
    "Notification",
    "WebhookEvent",
]

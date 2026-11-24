"""Add GitHub authentication, repository ingestion, and webhook events schema.

Revision ID: 002_add_github_auth_and_ingestion
Revises: 001_initial_schema
Create Date: 2026-11-03 10:00:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002_add_github_auth_and_ingestion"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update Users Table with GitHub credentials
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("github_id", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("github_access_token", sa.String(length=512), nullable=True))
        batch_op.create_index("ix_users_github_id", ["github_id"], unique=True)

    # 2. Update Repositories Table with Ingestion and Ownership tracking
    with op.batch_alter_table("repositories") as batch_op:
        batch_op.add_column(sa.Column("owner_user_id", sa.Uuid(), nullable=True))
        batch_op.add_column(sa.Column("language", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("stars_count", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("last_ingested_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("ingestion_status", sa.String(length=32), nullable=False, server_default="NOT_INGESTED"))
        batch_op.add_column(sa.Column("file_count", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("source_file_count", sa.Integer(), nullable=False, server_default="0"))
        batch_op.create_foreign_key("fk_repositories_owner_user", "users", ["owner_user_id"], ["id"], ondelete="SET NULL")
        batch_op.create_index("ix_repositories_owner", ["owner_user_id"])

    # 3. Create repository_files Table
    op.create_table(
        "repository_files",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("repository_id", sa.Uuid(), nullable=False),
        sa.Column("path", sa.String(length=1024), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("extension", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("size_bytes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("file_type", sa.String(length=32), nullable=False, server_default="source"),
        sa.Column("blob_sha", sa.String(length=64), nullable=True),
        sa.Column("branch", sa.String(length=128), nullable=False, server_default="main"),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("is_binary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("last_ingested_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("repository_id", "path", name="uq_repo_file_path"),
    )
    op.create_index("ix_repository_files_repository_id", "repository_files", ["repository_id"], unique=False)
    op.create_index("ix_repository_files_path", "repository_files", ["path"], unique=False)
    op.create_index("ix_repository_files_repo_type", "repository_files", ["repository_id", "file_type"], unique=False)
    op.create_index("ix_repository_files_repo_ext", "repository_files", ["repository_id", "extension"], unique=False)

    # 4. Create repository_ingestion_jobs Table
    op.create_table(
        "repository_ingestion_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("repository_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="PENDING"),
        sa.Column("branch", sa.String(length=128), nullable=False, server_default="main"),
        sa.Column("commit_sha", sa.String(length=64), nullable=True),
        sa.Column("total_files", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("source_files", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ignored_files", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_bytes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_repository_ingestion_jobs_repository_id", "repository_ingestion_jobs", ["repository_id"], unique=False)
    op.create_index("ix_repository_ingestion_jobs_status", "repository_ingestion_jobs", ["status"], unique=False)
    op.create_index("ix_repository_ingestion_jobs_created_at", "repository_ingestion_jobs", ["created_at"], unique=False)
    op.create_index("ix_ingestion_jobs_repo_status", "repository_ingestion_jobs", ["repository_id", "status"], unique=False)
    op.create_index("ix_ingestion_jobs_status_created", "repository_ingestion_jobs", ["status", "created_at"], unique=False)

    # 5. Create webhook_events Table
    op.create_table(
        "webhook_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("delivery_id", sa.String(length=128), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("repository_name", sa.String(length=255), nullable=True),
        sa.Column("payload_summary", sa.Text(), nullable=True),
        sa.Column("processed", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_webhook_events_delivery_id", "webhook_events", ["delivery_id"], unique=True)
    op.create_index("ix_webhook_events_event_type", "webhook_events", ["event_type"], unique=False)
    op.create_index("ix_webhook_events_repository_name", "webhook_events", ["repository_name"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_webhook_events_repository_name", table_name="webhook_events")
    op.drop_index("ix_webhook_events_event_type", table_name="webhook_events")
    op.drop_index("ix_webhook_events_delivery_id", table_name="webhook_events")
    op.drop_table("webhook_events")

    op.drop_index("ix_ingestion_jobs_status_created", table_name="repository_ingestion_jobs")
    op.drop_index("ix_ingestion_jobs_repo_status", table_name="repository_ingestion_jobs")
    op.drop_index("ix_repository_ingestion_jobs_created_at", table_name="repository_ingestion_jobs")
    op.drop_index("ix_repository_ingestion_jobs_status", table_name="repository_ingestion_jobs")
    op.drop_index("ix_repository_ingestion_jobs_repository_id", table_name="repository_ingestion_jobs")
    op.drop_table("repository_ingestion_jobs")

    op.drop_index("ix_repository_files_repo_ext", table_name="repository_files")
    op.drop_index("ix_repository_files_repo_type", table_name="repository_files")
    op.drop_index("ix_repository_files_path", table_name="repository_files")
    op.drop_index("ix_repository_files_repository_id", table_name="repository_files")
    op.drop_table("repository_files")

    with op.batch_alter_table("repositories") as batch_op:
        batch_op.drop_index("ix_repositories_owner")
        batch_op.drop_constraint("fk_repositories_owner_user", type_="foreignkey")
        batch_op.drop_column("source_file_count")
        batch_op.drop_column("file_count")
        batch_op.drop_column("ingestion_status")
        batch_op.drop_column("last_ingested_at")
        batch_op.drop_column("stars_count")
        batch_op.drop_column("language")
        batch_op.drop_column("owner_user_id")

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_index("ix_users_github_id")
        batch_op.drop_column("github_access_token")
        batch_op.drop_column("github_id")


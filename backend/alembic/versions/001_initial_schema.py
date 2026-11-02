"""Initial schema migration with users, organizations, members, repositories, and scan jobs.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-11-02 11:15:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Users Table
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("avatar_url", sa.String(length=1024), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    # 2. Organizations Table
    op.create_table(
        "organizations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_organizations_slug", "organizations", ["slug"], unique=True)

    # 3. Organization Members Table
    op.create_table(
        "organization_members",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="MEMBER"),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "organization_id", name="uq_org_member"),
    )
    op.create_index("ix_organization_members_organization_id", "organization_members", ["organization_id"], unique=False)
    op.create_index("ix_organization_members_user_id", "organization_members", ["user_id"], unique=False)

    # 4. Repositories Table
    op.create_table(
        "repositories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=512), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("provider", sa.String(length=64), nullable=False, server_default="github"),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("html_url", sa.String(length=1024), nullable=True),
        sa.Column("default_branch", sa.String(length=128), nullable=False, server_default="main"),
        sa.Column("is_private", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_scanned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "name", name="uq_org_repo_name"),
    )
    op.create_index("ix_repositories_organization_id", "repositories", ["organization_id"], unique=False)
    op.create_index("ix_repositories_name", "repositories", ["name"], unique=False)
    op.create_index("ix_repositories_full_name", "repositories", ["full_name"], unique=False)
    op.create_index("ix_repositories_provider", "repositories", ["provider"], unique=False)
    op.create_index("ix_repositories_external_id", "repositories", ["external_id"], unique=False)
    op.create_index("ix_repositories_is_active", "repositories", ["is_active"], unique=False)
    op.create_index("ix_repositories_is_private", "repositories", ["is_private"], unique=False)
    op.create_index("ix_repositories_org_active", "repositories", ["organization_id", "is_active"], unique=False)
    op.create_index("ix_repositories_provider_ext", "repositories", ["provider", "external_id"], unique=False)

    # 5. Scan Jobs Table
    op.create_table(
        "scan_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("repository_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="PENDING"),
        sa.Column("scan_type", sa.String(length=64), nullable=False, server_default="full"),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_scan_jobs_repository_id", "scan_jobs", ["repository_id"], unique=False)
    op.create_index("ix_scan_jobs_status", "scan_jobs", ["status"], unique=False)
    op.create_index("ix_scan_jobs_scan_type", "scan_jobs", ["scan_type"], unique=False)
    op.create_index("ix_scan_jobs_created_at", "scan_jobs", ["created_at"], unique=False)
    op.create_index("ix_scan_jobs_repo_status", "scan_jobs", ["repository_id", "status"], unique=False)
    op.create_index("ix_scan_jobs_status_created", "scan_jobs", ["status", "created_at"], unique=False)


def downgrade() -> None:
    # Drop tables in reverse dependency order
    op.drop_index("ix_scan_jobs_status_created", table_name="scan_jobs")
    op.drop_index("ix_scan_jobs_repo_status", table_name="scan_jobs")
    op.drop_index("ix_scan_jobs_created_at", table_name="scan_jobs")
    op.drop_index("ix_scan_jobs_scan_type", table_name="scan_jobs")
    op.drop_index("ix_scan_jobs_status", table_name="scan_jobs")
    op.drop_index("ix_scan_jobs_repository_id", table_name="scan_jobs")
    op.drop_table("scan_jobs")

    op.drop_index("ix_repositories_provider_ext", table_name="repositories")
    op.drop_index("ix_repositories_org_active", table_name="repositories")
    op.drop_index("ix_repositories_is_private", table_name="repositories")
    op.drop_index("ix_repositories_is_active", table_name="repositories")
    op.drop_index("ix_repositories_external_id", table_name="repositories")
    op.drop_index("ix_repositories_provider", table_name="repositories")
    op.drop_index("ix_repositories_full_name", table_name="repositories")
    op.drop_index("ix_repositories_name", table_name="repositories")
    op.drop_index("ix_repositories_organization_id", table_name="repositories")
    op.drop_table("repositories")

    op.drop_index("ix_organization_members_user_id", table_name="organization_members")
    op.drop_index("ix_organization_members_organization_id", table_name="organization_members")
    op.drop_table("organization_members")

    op.drop_index("ix_organizations_slug", table_name="organizations")
    op.drop_table("organizations")

    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

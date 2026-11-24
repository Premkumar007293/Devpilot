# Backup and Recovery Guide

## Overview
DevPilot stores application data primarily in SQLite for local development and PostgreSQL for production-friendly beta environments.

## Database backup

### SQLite local development
- Stop the backend service if a clean backup is required.
- Copy the SQLite database file.
- Optionally archive the vector index file used for repository retrieval.

Example:

```powershell
Copy-Item .\backend\devpilot.db .\backups\devpilot.db.bak
```

### PostgreSQL beta environments
- Use `pg_dump` for a logical backup.
- Schedule nightly or pre-release backups.
- Archive dump files with retention and encryption.

Example:

```bash
pg_dump -U devpilot -d devpilot_db > backup.sql
```

## Recovery guidance
1. Restore the database backup to the target environment.
2. Reapply any required Alembic migrations.
3. Rebuild vector indexes if they are missing or stale.
4. Re-run repository ingestion if repository metadata or file content is incomplete.
5. Verify auth, repo connection, and health endpoints after restore.

## Vector index recovery
- Vector indexes are reconstructed from repository metadata and file content.
- If the database is restored without the vector files, re-index repositories via ingestion or repository refresh.

## User account recovery
- Keep a secure record of user account metadata in the application database.
- For production or beta accounts, use verified admin recovery flows rather than resetting secrets without authorization.

## Secret handling
Do not back up GitHub tokens, AI keys, or secret material as ordinary application data.
Store them separately in secure environment variables or vault-managed secrets.

## Limitations
- SQLite backups are simpler but not equivalent to managed PostgreSQL failover.
- Recovery of repository indexing depends on source availability and the repository being re-ingested.

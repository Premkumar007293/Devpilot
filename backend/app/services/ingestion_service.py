"""Repository ingestion engine parsing git tree structures and cataloging source code metadata."""

import asyncio
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.database.session import SessionLocal
from app.integrations.github.client import GitHubAPIException, GitHubClient
from app.models.repository import Repository
from app.models.repository_file import RepositoryFile
from app.models.repository_ingestion_job import IngestionStatus, RepositoryIngestionJob
from app.models.user import User
from app.workers.dispatcher import _local_executor

IGNORED_DIRS: Set[str] = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".next",
    ".nuxt",
    ".output",
    "target",
    "vendor",
    ".idea",
    ".vscode",
    "out",
    "bin",
    "obj",
}

IGNORED_EXTS: Set[str] = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".so",
    ".dll",
    ".dylib",
    ".exe",
    ".bin",
    ".iso",
    ".zip",
    ".tar",
    ".gz",
    ".7z",
    ".rar",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".svg",
    ".webp",
    ".mp4",
    ".mp3",
    ".pdf",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".lock",
    ".log",
    ".map",
}

SOURCE_EXTS: Set[str] = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".go",
    ".rs",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".cs",
    ".rb",
    ".php",
    ".swift",
    ".kt",
    ".scala",
    ".html",
    ".css",
    ".scss",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".md",
    ".sql",
    ".sh",
    ".dockerfile",
}


def is_path_ignored(path: str) -> bool:
    """Determine whether path matches common exclusion directories."""
    parts = path.replace("\\", "/").split("/")
    for part in parts[:-1]:
        if part in IGNORED_DIRS:
            return True
    return False


def get_file_type_and_binary(filename: str, ext: str) -> Tuple[str, bool]:
    """Classify file type and identify if binary asset."""
    ext_lower = ext.lower()
    if ext_lower in IGNORED_EXTS:
        return "asset", True
    if ext_lower in SOURCE_EXTS:
        if ext_lower in {".json", ".yaml", ".yml", ".toml"}:
            return "config", False
        if ext_lower in {".md"}:
            return "doc", False
        return "source", False
    return "other", False


class IngestionService:
    """Service executing and managing repository tree ingestion pipelines."""

    @staticmethod
    def start_ingestion(
        db: Session,
        repository_id: uuid.UUID,
        user: User,
        branch: Optional[str] = None,
        dispatch_async: bool = True,
    ) -> RepositoryIngestionJob:
        """Initialize ingestion job record and dispatch background processing."""
        repo = db.get(Repository, repository_id)
        if not repo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")

        target_branch = branch or repo.default_branch or "main"
        access_token = user.github_access_token
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User GitHub access token is not available for repository ingestion",
            )

        # Create job tracking entry
        job = RepositoryIngestionJob(
            repository_id=repo.id,
            status=IngestionStatus.QUEUED.value,
            branch=target_branch,
            progress=5,
        )
        db.add(job)
        repo.ingestion_status = "IN_PROGRESS"
        db.commit()
        db.refresh(job)

        logger.info("Created ingestion job id=%s for repo=%s branch=%s", job.id, repo.full_name, target_branch)

        if dispatch_async:
            _local_executor.submit(
                IngestionService._execute_ingestion_pipeline,
                str(job.id),
                str(repo.id),
                access_token,
                repo.full_name,
                target_branch,
            )
        else:
            IngestionService._execute_ingestion_pipeline(
                str(job.id),
                str(repo.id),
                access_token,
                repo.full_name,
                target_branch,
                db=db,
            )

        return job

    @staticmethod
    def _execute_ingestion_pipeline(
        job_id_str: str,
        repo_id_str: str,
        access_token: str,
        repo_full_name: str,
        branch: str,
        db: Optional[Session] = None,
    ) -> None:
        """Execute git tree fetching, filtering, and database persistence."""
        logger.info("Executing ingestion pipeline for job=%s repo=%s", job_id_str, repo_full_name)
        own_db = False
        if db is None:
            db = SessionLocal()
            own_db = True

        job_uuid = uuid.UUID(job_id_str)
        repo_uuid = uuid.UUID(repo_id_str)
        job = db.get(RepositoryIngestionJob, job_uuid)
        repo = db.get(Repository, repo_uuid)

        if not job or not repo:
            if own_db and db:
                db.close()
            return

        try:
            job.status = IngestionStatus.RUNNING.value
            job.started_at = datetime.now(timezone.utc)
            job.progress = 20
            db.commit()

            # Parse owner and repo name from full_name
            parts = repo_full_name.split("/")
            if len(parts) == 2:
                owner, repo_name = parts[0], parts[1]
            else:
                owner, repo_name = repo.name, repo.name

            # Query GitHub git trees recursively
            gh_client = GitHubClient(token=access_token)
            loop = asyncio.new_event_loop()
            try:
                tree_data = loop.run_until_complete(
                    gh_client.get_repository_tree(owner=owner, repo=repo_name, branch=branch)
                )
            finally:
                pass

            job.progress = 50
            db.commit()

            raw_tree = tree_data.get("tree", [])
            commit_sha = tree_data.get("sha")
            if commit_sha:
                job.commit_sha = commit_sha

            # Filter and categorize tree entries
            total_count = 0
            source_count = 0
            ignored_count = 0
            total_bytes = 0

            # Delete previous file index for re-ingestion
            db.execute(delete(RepositoryFile).where(RepositoryFile.repository_id == repo.id))
            db.commit()

            file_objects: List[RepositoryFile] = []
            for item in raw_tree:
                if item.get("type") != "blob":
                    continue  # We only index files, directories are implicit from paths

                path = item.get("path", "")
                if is_path_ignored(path):
                    ignored_count += 1
                    continue

                filename = os.path.basename(path)
                _, ext = os.path.splitext(filename)
                file_type, is_binary = get_file_type_and_binary(filename, ext)

                if is_binary:
                    ignored_count += 1
                    continue

                size = item.get("size", 0)
                total_count += 1
                total_bytes += size
                if file_type == "source":
                    source_count += 1

                file_record = RepositoryFile(
                    repository_id=repo.id,
                    path=path,
                    name=filename,
                    extension=ext.lower(),
                    size_bytes=size,
                    file_type=file_type,
                    blob_sha=item.get("sha"),
                    branch=branch,
                    is_binary=False,
                    last_ingested_at=datetime.now(timezone.utc),
                )

                if file_type in {"source", "config", "doc"}:
                    try:
                        file_content = loop.run_until_complete(
                            gh_client.get_file_contents(owner=owner, repo=repo_name, path=path, ref=branch)
                        )
                        if file_content is not None:
                            file_record.content = file_content
                    except Exception:
                        logger.debug("Failed to fetch file contents for %s in repository %s", path, repo_full_name)

                file_objects.append(file_record)

            job.progress = 75
            db.commit()

            # Bulk insert files in batches
            batch_size = 500
            for i in range(0, len(file_objects), batch_size):
                db.add_all(file_objects[i : i + batch_size])
                db.commit()

            # Finalize metrics
            job.total_files = total_count
            job.source_files = source_count
            job.ignored_files = ignored_count
            job.total_bytes = total_bytes
            job.status = IngestionStatus.COMPLETED.value
            job.progress = 100
            job.completed_at = datetime.now(timezone.utc)

            repo.ingestion_status = "COMPLETED"
            repo.file_count = total_count
            repo.source_file_count = source_count
            repo.last_ingested_at = datetime.now(timezone.utc)
            db.commit()

            logger.info(
                "Ingestion completed for repo %s: %s files (%s source) indexed.",
                repo_full_name,
                total_count,
                source_count,
            )

        except Exception as exc:
            logger.error("Ingestion failed for job %s: %s", job_id_str, str(exc))
            try:
                job.status = IngestionStatus.FAILED.value
                job.error_message = str(exc)
                job.completed_at = datetime.now(timezone.utc)
                repo.ingestion_status = "FAILED"
                db.commit()
            except Exception:
                db.rollback()
        finally:
            try:
                loop.close()
            except Exception:
                pass
            if own_db and db:
                db.close()


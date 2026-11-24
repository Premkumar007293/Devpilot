"""Service layer for advanced repository engineering intelligence."""

from __future__ import annotations

import uuid
from typing import Any, Dict, Iterable, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.engines.analyzer.advanced import (
    CodeUnderstandingEngine,
    DebuggingAssistant,
    RefactoringAdvisor,
    TestGenerationEngine,
)
from app.models.repository import Repository
from app.models.repository_file import RepositoryFile


class AIEngineeringService:
    """Repository-aware engineering intelligence facade."""

    @staticmethod
    def _repository_files(db: Session, repository_id: uuid.UUID) -> list[dict[str, Any]]:
        rows = db.scalars(
            select(RepositoryFile)
            .where(RepositoryFile.repository_id == repository_id)
            .order_by(RepositoryFile.path.asc())
        ).all()
        return [{"path": file.path, "content": file.content or ""} for file in rows]

    @staticmethod
    def understand_repository(db: Session, repository_id: uuid.UUID) -> Dict[str, Any]:
        repo = db.get(Repository, repository_id)
        if repo is None:
            raise ValueError(f"Repository {repository_id} not found")
        files = AIEngineeringService._repository_files(db, repository_id)
        result = CodeUnderstandingEngine.analyze_repository(files)
        result["repository_id"] = str(repo.id)
        return result

    @staticmethod
    def debug_repository_issue(db: Session, repository_id: uuid.UUID, problem_description: str) -> Dict[str, Any]:
        repo = db.get(Repository, repository_id)
        if repo is None:
            raise ValueError(f"Repository {repository_id} not found")
        files = AIEngineeringService._repository_files(db, repository_id)
        return DebuggingAssistant.debug_issue(files, problem_description)

    @staticmethod
    def recommend_refactors(db: Session, repository_id: uuid.UUID) -> list[Dict[str, Any]]:
        repo = db.get(Repository, repository_id)
        if repo is None:
            raise ValueError(f"Repository {repository_id} not found")
        files = AIEngineeringService._repository_files(db, repository_id)
        return RefactoringAdvisor.recommend_refactors(files)

    @staticmethod
    def generate_tests(db: Session, repository_id: uuid.UUID, target_symbol: Optional[str] = None) -> Dict[str, Any]:
        repo = db.get(Repository, repository_id)
        if repo is None:
            raise ValueError(f"Repository {repository_id} not found")
        files = AIEngineeringService._repository_files(db, repository_id)
        return TestGenerationEngine.generate_tests(files, target_symbol=target_symbol)


__all__ = ["AIEngineeringService"]

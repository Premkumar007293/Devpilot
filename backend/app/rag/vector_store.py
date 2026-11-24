"""Persistent local vector storage for repository chunk retrieval."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from app.core.config import settings
from app.rag.models import Citation, CodeChunk, RetrievalResult


def _cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if not left or not right:
        return 0.0
    left_norm = sum(v * v for v in left) ** 0.5
    right_norm = sum(v * v for v in right) ** 0.5
    if left_norm == 0 or right_norm == 0:
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    return dot / (left_norm * right_norm)


class LocalVectorStore:
    """Local SQLite-backed vector store for repository indexing and semantic retrieval."""

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or settings.VECTOR_DB_PATH
        base_path = Path(self.db_path)
        base_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _initialize(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS rag_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repository_id TEXT NOT NULL,
                    file_id TEXT,
                    file_path TEXT NOT NULL,
                    language TEXT NOT NULL,
                    symbol_name TEXT,
                    symbol_type TEXT,
                    start_line INTEGER,
                    end_line INTEGER,
                    content_hash TEXT NOT NULL,
                    chunk_content TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    chunking_version TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(repository_id, content_hash)
                )
                """
            )
            connection.commit()

    def create_collection(self, repository_id: str) -> None:
        """Repository-specific collection creation is represented by a repository_id filter."""
        return None

    def add_chunk(self, chunk: CodeChunk) -> None:
        if chunk.embedding is None:
            chunk.embedding = []
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO rag_chunks (
                    repository_id,
                    file_id,
                    file_path,
                    language,
                    symbol_name,
                    symbol_type,
                    start_line,
                    end_line,
                    content_hash,
                    chunk_content,
                    embedding,
                    chunking_version,
                    metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(chunk.repository_id),
                    chunk.file_id,
                    chunk.file_path,
                    chunk.language,
                    chunk.symbol_name,
                    chunk.symbol_type,
                    chunk.start_line,
                    chunk.end_line,
                    chunk.content_hash,
                    chunk.chunk_content,
                    json.dumps(chunk.embedding),
                    chunk.chunking_version,
                    json.dumps(chunk.metadata),
                ),
            )
            connection.commit()

    def add_chunks(self, chunks: Iterable[CodeChunk]) -> None:
        for chunk in chunks:
            self.add_chunk(chunk)

    def _fetch_repository_rows(self, repository_id: str) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT repository_id, file_id, file_path, language, symbol_name, symbol_type,
                       start_line, end_line, content_hash, chunk_content, embedding,
                       chunking_version, metadata
                FROM rag_chunks
                WHERE repository_id = ?
                ORDER BY created_at DESC
                """,
                (str(repository_id),),
            ).fetchall()
        records: List[Dict[str, Any]] = []
        for row in rows:
            records.append({
                "repository_id": row[0],
                "file_id": row[1],
                "file_path": row[2],
                "language": row[3],
                "symbol_name": row[4],
                "symbol_type": row[5],
                "start_line": row[6],
                "end_line": row[7],
                "content_hash": row[8],
                "chunk_content": row[9],
                "embedding": json.loads(row[10]),
                "chunking_version": row[11],
                "metadata": json.loads(row[12]) if row[12] else {},
            })
        return records

    def search(
        self,
        query_embedding: Sequence[float],
        repository_id: str,
        *,
        top_k: int = 5,
        similarity_threshold: float = 0.0,
        per_file_limit: int = 2,
    ) -> List[RetrievalResult]:
        results: List[Tuple[float, Dict[str, Any]]] = []
        rows = self._fetch_repository_rows(repository_id)
        per_file_counts: Dict[str, int] = {}

        for row in rows:
            embedding = row["embedding"]
            score = _cosine_similarity(list(query_embedding), embedding)
            if score < similarity_threshold:
                continue
            file_path = row["file_path"]
            per_file_counts[file_path] = per_file_counts.get(file_path, 0) + 1
            if per_file_counts[file_path] > per_file_limit:
                continue
            results.append((score, row))

        results.sort(key=lambda item: item[0], reverse=True)
        retrieval_results: List[RetrievalResult] = []
        for score, row in results[:top_k]:
            chunk = CodeChunk(
                repository_id=row["repository_id"],
                file_id=row["file_id"],
                file_path=row["file_path"],
                language=row["language"],
                symbol_name=row["symbol_name"],
                symbol_type=row["symbol_type"],
                start_line=row["start_line"],
                end_line=row["end_line"],
                chunk_content=row["chunk_content"],
                content_hash=row["content_hash"],
                chunking_version=row["chunking_version"],
                metadata=row.get("metadata", {}),
                embedding=row["embedding"],
            )
            retrieval_results.append(
                RetrievalResult(
                    chunk=chunk,
                    score=float(score),
                    citation=Citation(
                        file_path=chunk.file_path,
                        start_line=chunk.start_line,
                        end_line=chunk.end_line,
                        symbol_name=chunk.symbol_name,
                        symbol_type=chunk.symbol_type,
                        score=float(score),
                    ),
                )
            )
        return retrieval_results

    def delete_repository(self, repository_id: str) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("DELETE FROM rag_chunks WHERE repository_id = ?", (str(repository_id),))
            connection.commit()

    def count_chunks(self, repository_id: str) -> int:
        with sqlite3.connect(self.db_path) as connection:
            return int(
                connection.execute(
                    "SELECT COUNT(*) FROM rag_chunks WHERE repository_id = ?",
                    (str(repository_id),),
                ).fetchone()[0]
            )

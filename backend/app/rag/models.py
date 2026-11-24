"""Dataclasses used across the repository RAG pipeline."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CodeChunk:
    """A semantically meaningful repository chunk used for retrieval."""

    repository_id: str
    file_path: str
    language: str = "python"
    symbol_name: Optional[str] = None
    symbol_type: str = "module"
    start_line: int = 1
    end_line: int = 1
    chunk_content: str = ""
    content_hash: str = ""
    chunking_version: str = "v1"
    file_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None

    def __post_init__(self) -> None:
        if not self.content_hash:
            self.content_hash = hashlib.sha256(self.chunk_content.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "repository_id": self.repository_id,
            "file_id": self.file_id,
            "file_path": self.file_path,
            "language": self.language,
            "symbol_name": self.symbol_name,
            "symbol_type": self.symbol_type,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "chunk_content": self.chunk_content,
            "content_hash": self.content_hash,
            "chunking_version": self.chunking_version,
            "metadata": self.metadata,
        }
        if self.embedding is not None:
            data["embedding"] = self.embedding
        return data

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "CodeChunk":
        return cls(
            repository_id=str(payload["repository_id"]),
            file_path=payload["file_path"],
            language=payload.get("language", "python"),
            symbol_name=payload.get("symbol_name"),
            symbol_type=payload.get("symbol_type", "module"),
            start_line=int(payload.get("start_line", 1)),
            end_line=int(payload.get("end_line", 1)),
            chunk_content=payload.get("chunk_content", ""),
            content_hash=payload.get("content_hash", ""),
            chunking_version=payload.get("chunking_version", "v1"),
            file_id=payload.get("file_id"),
            metadata=payload.get("metadata", {}),
            embedding=payload.get("embedding"),
        )


@dataclass
class Citation:
    """Source citation for a retrieval result."""

    file_path: str
    start_line: int
    end_line: int
    symbol_name: Optional[str] = None
    symbol_type: str = "module"
    score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "symbol_name": self.symbol_name,
            "symbol_type": self.symbol_type,
            "score": self.score,
        }


@dataclass
class RetrievalResult:
    """A retrieved chunk and its citation metadata."""

    chunk: CodeChunk
    score: float
    citation: Citation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "chunk": self.chunk.to_dict(),
            "citation": self.citation.to_dict(),
        }


@dataclass
class ContextBundle:
    """Repository-grounded prompt payload ready for the LLM."""

    question: str
    context_text: str
    citations: List[Citation]

"""Code chunking logic for repository indexing."""

from __future__ import annotations

import ast
import hashlib
import re
from pathlib import Path
from typing import Iterable, List, Sequence

from app.rag.models import CodeChunk


class CodeChunker:
    """Build semantically meaningful chunks from repository source files."""

    def __init__(self, chunk_size: int = 1200, overlap: int = 150, chunking_version: str = "v1"):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.chunking_version = chunking_version

    @staticmethod
    def detect_language(file_path: str) -> str:
        suffix = Path(file_path).suffix.lower()
        mapping = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".go": "go",
            ".rs": "rust",
            ".java": "java",
            ".cs": "csharp",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".sql": "sql",
            ".md": "markdown",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".sh": "bash",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
        }
        return mapping.get(suffix, "text")

    @staticmethod
    def _normalize_chunk_content(content: str) -> str:
        return "\n".join(line.rstrip() for line in content.splitlines()).strip()

    def _hash_content(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _fallback_chunk(self, content: str, *, file_path: str, repository_id: str, file_id: str | None, language: str) -> List[CodeChunk]:
        normalized = self._normalize_chunk_content(content)
        if not normalized:
            return []
        lines = normalized.splitlines()
        chunks: List[CodeChunk] = []
        for i in range(0, len(lines), self.chunk_size):
            window = lines[i : i + self.chunk_size]
            chunk_text = "\n".join(window).strip()
            if not chunk_text:
                continue
            start_line = i + 1
            end_line = i + len(window)
            chunks.append(
                CodeChunk(
                    repository_id=repository_id,
                    file_id=file_id,
                    file_path=file_path,
                    language=language,
                    symbol_name=None,
                    symbol_type="module",
                    start_line=start_line,
                    end_line=end_line,
                    chunk_content=chunk_text,
                    content_hash=self._hash_content(chunk_text),
                    chunking_version=self.chunking_version,
                )
            )
        return chunks

    def _chunk_python(self, file_path: str, content: str, *, repository_id: str, file_id: str | None) -> List[CodeChunk]:
        try:
            module = ast.parse(content)
        except SyntaxError:
            return self._fallback_chunk(content, file_path=file_path, repository_id=repository_id, file_id=file_id, language="python")

        chunks: List[CodeChunk] = []
        seen: set[tuple[int, int, str]] = set()
        for node in module.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start_line = node.lineno
                end_line = node.end_lineno or node.lineno
                chunk_text = self._normalize_chunk_content("\n".join(content.splitlines()[start_line - 1 : end_line]))
                if not chunk_text:
                    continue
                key = (start_line, end_line, node.name)
                if key in seen:
                    continue
                seen.add(key)
                chunks.append(
                    CodeChunk(
                        repository_id=repository_id,
                        file_id=file_id,
                        file_path=file_path,
                        language="python",
                        symbol_name=node.name,
                        symbol_type="class" if isinstance(node, ast.ClassDef) else "function",
                        start_line=start_line,
                        end_line=end_line,
                        chunk_content=chunk_text,
                        content_hash=self._hash_content(chunk_text),
                        chunking_version=self.chunking_version,
                    )
                )

        if not chunks:
            return self._fallback_chunk(content, file_path=file_path, repository_id=repository_id, file_id=file_id, language="python")

        return chunks

    def _chunk_generic(self, file_path: str, content: str, *, repository_id: str, file_id: str | None, language: str) -> List[CodeChunk]:
        normalized = self._normalize_chunk_content(content)
        if not normalized:
            return []

        lines = normalized.splitlines()
        chunked: List[CodeChunk] = []
        for start in range(0, len(lines), max(1, self.chunk_size - self.overlap)):
            window = lines[start : start + self.chunk_size]
            if not window:
                continue
            chunk_text = "\n".join(window).strip()
            if not chunk_text:
                continue
            chunked.append(
                CodeChunk(
                    repository_id=repository_id,
                    file_id=file_id,
                    file_path=file_path,
                    language=language,
                    symbol_name=None,
                    symbol_type="module",
                    start_line=start + 1,
                    end_line=start + len(window),
                    chunk_content=chunk_text,
                    content_hash=self._hash_content(chunk_text),
                    chunking_version=self.chunking_version,
                )
            )
        return chunked

    def chunk_file(self, file_path: str, content: str, *, repository_id: str, file_id: str | None = None) -> List[CodeChunk]:
        language = self.detect_language(file_path)
        if language == "python":
            return self._chunk_python(file_path, content, repository_id=repository_id, file_id=file_id)
        return self._chunk_generic(file_path, content, repository_id=repository_id, file_id=file_id, language=language)

    def chunk_files(self, repository_id: str, files: Iterable[dict]) -> List[CodeChunk]:
        """Chunk a sequence of repository file payloads."""
        chunks: List[CodeChunk] = []
        for file_payload in files:
            file_path = file_payload.get("path") or file_payload.get("file_path")
            content = file_payload.get("content") or ""
            file_id = file_payload.get("id") or file_payload.get("file_id")
            if not file_path or not content:
                continue
            chunks.extend(self.chunk_file(file_path, content, repository_id=repository_id, file_id=str(file_id) if file_id is not None else None))
        return chunks

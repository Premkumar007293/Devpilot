"""Semantic retrieval utilities for repository-aware question answering."""

from __future__ import annotations

from typing import Iterable, List, Sequence

from app.rag.citation_builder import build_citation
from app.rag.embeddings import BaseEmbeddingProvider, get_embedding_provider
from app.rag.models import CodeChunk, RetrievalResult
from app.rag.vector_store import LocalVectorStore


class CodeRetriever:
    """Query the local repository vector store and rank grounded chunk matches."""

    def __init__(
        self,
        vector_store: LocalVectorStore | None = None,
        embedding_provider: BaseEmbeddingProvider | None = None,
        *,
        top_k: int = 5,
        similarity_threshold: float = 0.0,
        per_file_limit: int = 2,
        max_context_size: int = 8000,
    ):
        self.vector_store = vector_store or LocalVectorStore()
        self.embedding_provider = embedding_provider or get_embedding_provider()
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.per_file_limit = per_file_limit
        self.max_context_size = max_context_size

    def _deduplicate(self, results: Iterable[RetrievalResult]) -> List[RetrievalResult]:
        deduped: List[RetrievalResult] = []
        seen: set[str] = set()
        for result in results:
            digest = f"{result.chunk.file_path}:{result.chunk.start_line}:{result.chunk.end_line}"
            if digest in seen:
                continue
            seen.add(digest)
            deduped.append(result)
        return deduped

    def retrieve(self, query: str, repository_id: str, **kwargs) -> List[RetrievalResult]:
        """Return the most relevant repository chunks for the query."""
        query_embedding = self.embedding_provider.embed_text(query)
        results = self.vector_store.search(
            query_embedding,
            repository_id,
            top_k=kwargs.get("top_k", self.top_k),
            similarity_threshold=kwargs.get("similarity_threshold", self.similarity_threshold),
            per_file_limit=kwargs.get("per_file_limit", self.per_file_limit),
        )

        scored = []
        for result in results:
            result.citation = build_citation(result.chunk, score=result.score)
            scored.append(result)

        if not scored:
            return []
        return self._deduplicate(scored)[: kwargs.get("top_k", self.top_k)]

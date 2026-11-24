"""Repository RAG pipeline orchestration."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Sequence

from app.core.config import settings
from app.engines.ai import get_ai_provider
from app.rag.chunker import CodeChunker
from app.rag.context_builder import ContextBuilder
from app.rag.embeddings import BaseEmbeddingProvider, get_embedding_provider
from app.rag.models import CodeChunk, ContextBundle, RetrievalResult
from app.rag.retriever import CodeRetriever
from app.rag.vector_store import LocalVectorStore


class RepoRAGPipeline:
    """Coordinate repository chunking, indexing, retrieval, and grounded answering."""

    def __init__(
        self,
        vector_store: LocalVectorStore | None = None,
        chunker: CodeChunker | None = None,
        embedding_provider: BaseEmbeddingProvider | None = None,
        retriever: CodeRetriever | None = None,
        context_builder: ContextBuilder | None = None,
    ):
        self.vector_store = vector_store or LocalVectorStore()
        self.chunker = chunker or CodeChunker()
        self.embedding_provider = embedding_provider or get_embedding_provider()
        self.retriever = retriever or CodeRetriever(vector_store=self.vector_store, embedding_provider=self.embedding_provider)
        self.context_builder = context_builder or ContextBuilder()

    def index_repository(self, repository_id: str, file_payloads: Iterable[dict]) -> List[CodeChunk]:
        """Convert repository file payloads into chunks and index them in the local vector store."""
        chunks = self.chunker.chunk_files(repository_id, file_payloads)
        for chunk in chunks:
            chunk.embedding = self.embedding_provider.embed_text(chunk.chunk_content)
        self.vector_store.add_chunks(chunks)
        return chunks

    def _build_repository_context(self, question: str, repository_id: str, repository_name: str, repository_full_name: str, default_branch: str) -> tuple[str, List[Dict[str, Any]], List[RetrievalResult]]:
        retrievals = self.retriever.retrieve(question, repository_id)
        bundle = self.context_builder.build(
            question,
            retrievals,
            repository_name=repository_name,
            repository_full_name=repository_full_name,
            default_branch=default_branch,
        )
        return bundle.context_text, [citation.to_dict() for citation in bundle.citations], retrievals

    def ask(
        self,
        question: str,
        repository_id: str,
        *,
        repository_name: str,
        repository_full_name: str,
        default_branch: str,
    ) -> Dict[str, Any]:
        """Answer a natural-language question using repository-grounded context."""
        context_text, citations, retrievals = self._build_repository_context(
            question,
            repository_id,
            repository_name,
            repository_full_name,
            default_branch,
        )

        if not retrievals:
            return {
                "answer": "I could not find repository context relevant to that question.",
                "citations": [],
                "retrieval_count": 0,
                "grounded": False,
            }

        selected_provider = get_ai_provider(settings.AI_CHAT_PROVIDER)
        try:
            answer = selected_provider.generate_completion(
                self.context_builder.system_prompt() + "\n\n" + self.context_builder.build(
                    question,
                    retrievals,
                    repository_name=repository_name,
                    repository_full_name=repository_full_name,
                    default_branch=default_branch,
                ).context_text,
                temperature=0.1,
                max_tokens=400,
            )
        except Exception:
            answer = (
                "I found repository evidence relevant to your question, but the AI chat provider is not configured. "
                "Use the retrieved citations below as the grounded source of truth."
            )

        return {
            "answer": answer,
            "citations": citations,
            "retrieval_count": len(retrievals),
            "grounded": True,
        }

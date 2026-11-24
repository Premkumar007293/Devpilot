"""Repository-aware retrieval-augmented generation (RAG) components."""

from app.rag.chunker import CodeChunker
from app.rag.context_builder import ContextBuilder
from app.rag.embeddings import BaseEmbeddingProvider, GeminiEmbeddingProvider, LocalEmbeddingProvider, OpenAIEmbeddingProvider
from app.rag.pipeline import RepoRAGPipeline
from app.rag.retriever import CodeRetriever
from app.rag.vector_store import LocalVectorStore

__all__ = [
    "BaseEmbeddingProvider",
    "CodeChunker",
    "CodeRetriever",
    "ContextBuilder",
    "GeminiEmbeddingProvider",
    "LocalEmbeddingProvider",
    "LocalVectorStore",
    "OpenAIEmbeddingProvider",
    "RepoRAGPipeline",
]

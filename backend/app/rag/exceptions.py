"""Exceptions used by repository RAG and vector retrieval components."""


class RAGException(RuntimeError):
    """Base class for repository RAG errors."""


class RepositoryIndexNotFoundError(RAGException):
    """Raised when a repository has no indexed context available."""


class MissingProviderConfigError(RAGException):
    """Raised when a configured provider is missing credentials or endpoint settings."""


class RetrievalError(RAGException):
    """Raised when retrieval or ranking fails."""

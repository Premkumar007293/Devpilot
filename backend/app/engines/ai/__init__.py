"""AI engines package providing multi-model AI abstraction."""

from app.core.config import settings
from app.engines.ai.base import BaseAIProvider
from app.engines.ai.gemini_provider import GeminiAIProvider
from app.engines.ai.openai_provider import OpenAIAIProvider


def get_ai_provider(provider_name: str = "openai") -> BaseAIProvider:
    """Factory function to instantiate configured AI provider."""
    normalized = (provider_name or settings.AI_CHAT_PROVIDER).lower().strip()
    if normalized == "gemini":
        return GeminiAIProvider(api_key=settings.GEMINI_API_KEY)
    if normalized in ("openai", "gpt"):
        return OpenAIAIProvider(api_key=settings.OPENAI_API_KEY)
    raise ValueError(f"Unsupported AI provider: {provider_name}")


def get_embedding_provider(provider_name: str | None = None):
    """Return a configured embedding provider for repository indexing."""
    normalized = (provider_name or settings.AI_EMBEDDING_PROVIDER).lower().strip()
    if normalized in ("local", "offline", "fallback"):
        from app.rag.embeddings import LocalEmbeddingProvider
        return LocalEmbeddingProvider()
    if normalized == "openai":
        from app.rag.embeddings import OpenAIEmbeddingProvider
        return OpenAIEmbeddingProvider()
    if normalized == "gemini":
        from app.rag.embeddings import GeminiEmbeddingProvider
        return GeminiEmbeddingProvider()
    raise ValueError(f"Unsupported embedding provider: {normalized}")


__all__ = [
    "BaseAIProvider",
    "GeminiAIProvider",
    "OpenAIAIProvider",
    "get_ai_provider",
    "get_embedding_provider",
]

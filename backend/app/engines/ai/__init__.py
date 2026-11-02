"""AI engines package providing multi-model AI abstraction."""

from app.engines.ai.base import BaseAIProvider
from app.engines.ai.gemini_provider import GeminiAIProvider
from app.engines.ai.openai_provider import OpenAIAIProvider
from app.core.config import settings


def get_ai_provider(provider_name: str = "gemini") -> BaseAIProvider:
    """Factory function to instantiate configured AI provider."""
    normalized = provider_name.lower().strip()
    if normalized == "gemini":
        return GeminiAIProvider(api_key=settings.GEMINI_API_KEY)
    elif normalized in ("openai", "gpt"):
        return OpenAIAIProvider(api_key=settings.OPENAI_API_KEY)
    raise ValueError(f"Unsupported AI provider: {provider_name}")


__all__ = ["BaseAIProvider", "GeminiAIProvider", "OpenAIAIProvider", "get_ai_provider"]

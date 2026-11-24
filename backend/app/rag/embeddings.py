"""Provider-independent embedding service implementations."""

from __future__ import annotations

import hashlib
import json
import math
import re
from typing import Iterable, List, Sequence

import httpx

from app.core.config import settings
from app.rag.exceptions import MissingProviderConfigError


class BaseEmbeddingProvider:
    """Abstract embedding provider contract."""

    name: str = "base"

    def embed_text(self, text: str, **kwargs) -> List[float]:
        vectors = self.embed_texts([text], **kwargs)
        if not vectors:
            return []
        return vectors[0]

    def embed_texts(self, texts: Sequence[str], **kwargs) -> List[List[float]]:
        raise NotImplementedError


class LocalEmbeddingProvider(BaseEmbeddingProvider):
    """Deterministic local embedding provider for offline development."""

    name = "local"
    dimension = 384

    def _tokenize(self, text: str) -> List[str]:
        return [token.lower() for token in re.findall(r"[A-Za-z0-9_]+", text) if token]

    def _hash_to_vector(self, text: str) -> List[float]:
        tokens = self._tokenize(text)
        vector = [0.0] * self.dimension
        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
            bucket = int(digest, 16) % self.dimension
            vector[bucket] += 1.0

        magnitude = math.sqrt(sum(value * value for value in vector))
        if magnitude:
            vector = [value / magnitude for value in vector]
        return vector

    def embed_texts(self, texts: Sequence[str], **kwargs) -> List[List[float]]:
        return [self._hash_to_vector(text) for text in texts]


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI embedding provider for remote embeddings with environment-backed credentials."""

    name = "openai"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_EMBEDDING_MODEL

    def embed_texts(self, texts: Sequence[str], **kwargs) -> List[List[float]]:
        if not self.api_key:
            raise MissingProviderConfigError("OpenAI embedding provider requires OPENAI_API_KEY.")
        response = httpx.post(
            "https://api.openai.com/v1/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "input": list(texts),
                "model": self.model,
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        return [item["embedding"] for item in payload.get("data", [])]


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    """Google Gemini embedding provider for local or remote embeddings."""

    name = "gemini"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_EMBEDDING_MODEL

    def embed_texts(self, texts: Sequence[str], **kwargs) -> List[List[float]]:
        if not self.api_key:
            raise MissingProviderConfigError("Gemini embedding provider requires GEMINI_API_KEY.")
        embeddings: List[List[float]] = []
        for text in texts:
            response = httpx.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:embedContent?key={self.api_key}",
                json={
                    "content": {"parts": [{"text": text}]},
                    "taskType": "RETRIEVAL_DOCUMENT",
                },
                timeout=30,
            )
            response.raise_for_status()
            payload = response.json()
            embedding = payload.get("embedding", {}).get("values") or []
            embeddings.append([float(value) for value in embedding])
        return embeddings


def get_embedding_provider(provider_name: str | None = None) -> BaseEmbeddingProvider:
    """Return an embedding provider based on configuration or explicit value."""
    normalized = (provider_name or settings.AI_EMBEDDING_PROVIDER).lower().strip()
    if normalized in {"local", "offline", "fallback"}:
        return LocalEmbeddingProvider()
    if normalized == "openai":
        return OpenAIEmbeddingProvider()
    if normalized == "gemini":
        return GeminiEmbeddingProvider()
    raise ValueError(f"Unsupported embedding provider: {provider_name or settings.AI_EMBEDDING_PROVIDER}")


__all__ = [
    "BaseEmbeddingProvider",
    "GeminiEmbeddingProvider",
    "LocalEmbeddingProvider",
    "OpenAIEmbeddingProvider",
    "get_embedding_provider",
]

"""Provider-independent AI architecture abstraction.

Defines unified interface for multi-model AI capabilities (Gemini, OpenAI, etc.).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseAIProvider(ABC):
    """Abstract Base Class for AI model integrations."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    @abstractmethod
    async def generate_completion(self, prompt: str, **kwargs: Any) -> str:
        """Generate general text completion."""
        pass

    @abstractmethod
    async def analyze_code(self, code_snippet: str, language: str) -> Dict[str, Any]:
        """Perform semantic code intelligence analysis."""
        pass

    @abstractmethod
    async def explain_architecture(self, repository_map: Dict[str, Any]) -> str:
        """Generate high-level architectural overview from code graph."""
        pass

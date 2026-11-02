"""Static code analysis and security engine abstractions."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseCodeAnalyzer(ABC):
    """Abstract Base Class for code intelligence and security analyzers."""

    @abstractmethod
    async def analyze_syntax(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse AST and evaluate syntax metrics."""
        pass

    @abstractmethod
    async def scan_vulnerabilities(self, source_path: str) -> List[Dict[str, Any]]:
        """Identify potential security vulnerabilities (e.g. CWE, OWASP Top 10)."""
        pass

    @abstractmethod
    async def calculate_complexity(self, content: str) -> Dict[str, Any]:
        """Compute cyclomatic and cognitive complexity metrics."""
        pass

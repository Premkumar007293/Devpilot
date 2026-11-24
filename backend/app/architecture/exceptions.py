"""Architecture analysis exceptions."""


class ArchitectureAnalysisError(RuntimeError):
    """Base exception for architecture inspection failures."""


class RepositoryNotAnalyzableError(ArchitectureAnalysisError):
    """Raised when a repository cannot be analyzed."""


class InvalidArchitectureNodeError(ArchitectureAnalysisError):
    """Raised when a node or edge is malformed."""

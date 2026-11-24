"""Build citations for repository-grounded retrieval results."""

from typing import Iterable, List

from app.rag.models import Citation, CodeChunk


def build_citation(chunk: CodeChunk, score: float = 0.0) -> Citation:
    """Create a citation for a retrieved code chunk."""
    return Citation(
        file_path=chunk.file_path,
        start_line=chunk.start_line,
        end_line=chunk.end_line,
        symbol_name=chunk.symbol_name,
        symbol_type=chunk.symbol_type,
        score=score,
    )


def build_citations(chunks: Iterable[CodeChunk], scores: Iterable[float]) -> List[Citation]:
    """Build citations for a sequence of code chunks."""
    citations: List[Citation] = []
    for chunk, score in zip(chunks, scores):
        citations.append(build_citation(chunk, score=score))
    return citations

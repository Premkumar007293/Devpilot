"""Construct grounded prompts using the retrieved repository evidence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from app.rag.models import Citation, ContextBundle, RetrievalResult
from app.rag.prompt_templates import QUESTION_TEMPLATE, SYSTEM_TEMPLATE


class ContextBuilder:
    """Formats repository retrieval results into a grounded LLM prompt."""

    def __init__(self, max_context_chars: int = 12000):
        self.max_context_chars = max_context_chars

    def _render_retrievals(self, retrievals: Sequence[RetrievalResult]) -> str:
        lines: List[str] = []
        for index, result in enumerate(retrievals, start=1):
            chunk = result.chunk
            citation = result.citation or Citation(
                file_path=chunk.file_path,
                start_line=chunk.start_line,
                end_line=chunk.end_line,
                symbol_name=chunk.symbol_name,
                symbol_type=chunk.symbol_type,
                score=result.score,
            )
            snippet = chunk.chunk_content.strip().replace("\r\n", "\n")
            lines.append(
                f"[{index}] {citation.file_path}:{citation.start_line}-{citation.end_line} "
                f"({citation.symbol_type or 'module'}{f'::{citation.symbol_name}' if citation.symbol_name else ''})\n{snippet}"
            )
        return "\n\n".join(lines)

    def build(self, question: str, retrievals: Sequence[RetrievalResult], *, repository_name: str, repository_full_name: str, default_branch: str) -> ContextBundle:
        context_text = self._render_retrievals(retrievals)
        if len(context_text) > self.max_context_chars:
            context_text = context_text[: self.max_context_chars]
        prompt = QUESTION_TEMPLATE.format(
            question=question,
            repository_name=repository_name,
            repository_full_name=repository_full_name,
            default_branch=default_branch,
            context_text=context_text,
        )
        citations = [result.citation for result in retrievals if result.citation is not None]
        return ContextBundle(
            question=question,
            context_text=context_text,
            citations=citations,
        )

    def system_prompt(self) -> str:
        return SYSTEM_TEMPLATE

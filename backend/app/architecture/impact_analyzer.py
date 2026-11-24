"""Analyze change impact from a selected file or symbol."""

from __future__ import annotations

from collections import deque
from typing import Dict, List, Set


class ImpactAnalyzer:
    """Compute direct and transitive impact using the repository dependency graph."""

    @staticmethod
    def analyze(graph: Dict[str, List[str]], target: str) -> Dict[str, List[str] | List[dict] | str | float]:
        reverse_graph: Dict[str, List[str]] = {}
        for source, dependencies in graph.items():
            for dependency in dependencies:
                reverse_graph.setdefault(dependency, []).append(source)

        direct_dependents = sorted(set(reverse_graph.get(target, [])))
        queue = deque(direct_dependents)
        seen: Set[str] = set(direct_dependents)
        transitive: List[str] = []
        relationship_paths: List[dict] = []

        while queue:
            current = queue.popleft()
            for dependent in sorted(set(reverse_graph.get(current, []))):
                if dependent in seen:
                    continue
                seen.add(dependent)
                transitive.append(dependent)
                relationship_paths.append({"from": current, "to": dependent, "relationship": "reverse-dependency"})
                queue.append(dependent)

        if not direct_dependents and not transitive:
            risk_level = "low"
        elif len(direct_dependents) > 5 or len(transitive) > 10:
            risk_level = "high"
        elif len(direct_dependents) > 0 or len(transitive) > 0:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "target": target,
            "direct_dependents": direct_dependents,
            "transitive_dependents": sorted(set(transitive)),
            "relationship_paths": relationship_paths,
            "confidence": 0.8 if direct_dependents or transitive else 0.5,
            "risk_level": risk_level,
            "evidence": [
                f"{target} is referenced by {len(direct_dependents)} direct dependents" if direct_dependents else f"{target} has no direct dependents in the static graph",
            ],
        }

"""Cycle detection for dependency graphs."""

from __future__ import annotations

from typing import Dict, Iterable, List, Set, Tuple

from app.architecture.models import GraphCycle


class CycleDetector:
    """Detect strongly connected components in a dependency graph."""

    @staticmethod
    def detect(graph: Dict[str, List[str]]) -> List[GraphCycle]:
        index = 0
        stack: List[str] = []
        on_stack: Set[str] = set()
        indices: Dict[str, int] = {}
        lowlinks: Dict[str, int] = {}
        cycles: List[GraphCycle] = []

        def strongconnect(node: str):
            nonlocal index
            indices[node] = index
            lowlinks[node] = index
            index += 1
            stack.append(node)
            on_stack.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in indices:
                    strongconnect(neighbor)
                    lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
                elif neighbor in on_stack:
                    lowlinks[node] = min(lowlinks[node], indices[neighbor])

            if lowlinks[node] == indices[node]:
                component: List[str] = []
                while True:
                    current = stack.pop()
                    on_stack.remove(current)
                    component.append(current)
                    if current == node:
                        break
                if len(component) > 1:
                    chain = sorted(component)
                    cycles.append(
                        GraphCycle(
                            cycle_id=f"cycle:{len(cycles) + 1}",
                            participants=chain,
                            chain=chain,
                            cycle_length=len(chain),
                            severity='high' if len(chain) > 2 else 'medium',
                            remediation='Break the dependency loop by isolating shared contracts or invert the dependency.',
                        )
                    )

        for node in sorted(graph):
            if node not in indices:
                strongconnect(node)

        return cycles

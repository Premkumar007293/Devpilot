"""Serialization helpers for architecture graph payloads."""

from __future__ import annotations

from typing import Any, Iterable, List


class GraphSerializer:
    """Convert architecture graph objects into JSON-safe payloads."""

    @staticmethod
    def serialize_nodes(nodes: Iterable[Any]) -> List[dict]:
        return [node.to_dict() for node in nodes]

    @staticmethod
    def serialize_edges(edges: Iterable[Any]) -> List[dict]:
        return [edge.to_dict() for edge in edges]

    @staticmethod
    def serialize_layers(layers: Iterable[Any]) -> List[dict]:
        return [layer.to_dict() for layer in layers]

    @staticmethod
    def serialize_cycles(cycles: Iterable[Any]) -> List[dict]:
        return [cycle.to_dict() for cycle in cycles]

    @staticmethod
    def serialize_entrypoints(entrypoints: Iterable[Any]) -> List[dict]:
        return [entry.to_dict() for entry in entrypoints]

    @staticmethod
    def serialize_impact(impact: dict) -> dict:
        return {
            "target": impact.get("target"),
            "direct_dependents": impact.get("direct_dependents", []),
            "transitive_dependents": impact.get("transitive_dependents", []),
            "relationship_paths": impact.get("relationship_paths", []),
            "confidence": impact.get("confidence", 0.0),
            "risk_level": impact.get("risk_level", "unknown"),
            "evidence": impact.get("evidence", []),
        }

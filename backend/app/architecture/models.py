"""Architecture dataclasses used to serialize graph snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class GraphNode:
    """A repository node in the architecture graph."""

    node_id: str
    repository_id: str
    name: str
    path: str
    node_type: str
    language: str = "text"
    parent_node_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "repository_id": self.repository_id,
            "name": self.name,
            "path": self.path,
            "node_type": self.node_type,
            "language": self.language,
            "parent_node_id": self.parent_node_id,
            "metadata": self.metadata,
        }


@dataclass
class GraphEdge:
    """A directed dependency edge between architecture nodes."""

    edge_id: str
    source_node: str
    target_node: str
    relationship_type: str
    source_file: str
    source_line: Optional[int] = None
    confidence: float = 0.0
    detection_method: str = "static"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source_node": self.source_node,
            "target_node": self.target_node,
            "relationship_type": self.relationship_type,
            "source_file": self.source_file,
            "source_line": self.source_line,
            "confidence": self.confidence,
            "detection_method": self.detection_method,
            "metadata": self.metadata,
        }


@dataclass
class GraphCycle:
    """Detected strongly connected component cycle."""

    cycle_id: str
    participants: List[str]
    chain: List[str]
    cycle_length: int
    severity: str
    remediation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "participants": self.participants,
            "chain": self.chain,
            "cycle_length": self.cycle_length,
            "severity": self.severity,
            "remediation": self.remediation,
        }


@dataclass
class ArchitectureLayer:
    """A layer classification for a repository node."""

    file_path: str
    layer_name: str
    confidence: float
    evidence: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "layer_name": self.layer_name,
            "confidence": self.confidence,
            "evidence": self.evidence,
        }


@dataclass
class EntryPoint:
    """An application entry point."""

    file_path: str
    symbol_name: Optional[str]
    entry_type: str
    detection_evidence: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "symbol_name": self.symbol_name,
            "entry_type": self.entry_type,
            "detection_evidence": self.detection_evidence,
        }

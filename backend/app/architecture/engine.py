"""Repository architecture analysis engine."""

from __future__ import annotations

import json
import uuid
from collections import defaultdict
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.architecture.cycle_detector import CycleDetector
from app.architecture.dependency_analyzer import DependencyAnalyzer
from app.architecture.entrypoint_detector import EntrypointDetector
from app.architecture.graph_builder import GraphBuilder
from app.architecture.graph_serializer import GraphSerializer
from app.architecture.impact_analyzer import ImpactAnalyzer
from app.architecture.layer_detector import LayerDetector
from app.models.architecture_snapshot import ArchitectureSnapshot
from app.models.repository import Repository
from app.models.repository_file import RepositoryFile


class ArchitectureAnalyzer:
    """Build repository structure, dependency, layer, and impact graphs."""

    @staticmethod
    def _dependency_map(edges: List[Any]) -> Dict[str, List[str]]:
        graph: Dict[str, List[str]] = defaultdict(list)
        for edge in edges:
            source = edge.source_node
            target = edge.target_node
            if source and target and source != target and target not in graph[source]:
                graph[source].append(target)
        return dict(graph)

    def analyze_repository(self, db: Session, repository_id: uuid.UUID) -> Dict[str, Any]:
        repo = db.get(Repository, repository_id)
        if repo is None:
            raise ValueError(f"Repository {repository_id} not found")

        files = list(db.query(RepositoryFile).filter(RepositoryFile.repository_id == repository_id).all())
        file_records = [
            {
                'path': file.path,
                'content': file.content or '',
                'file_id': str(file.id),
            }
            for file in files
        ]

        all_paths = [record['path'] for record in file_records if record.get('path')]
        nodes, adjacency = GraphBuilder.build_hierarchy(str(repo.id), all_paths)
        edges = DependencyAnalyzer().analyze(file_records)
        dependency_map = self._dependency_map(edges)

        cycles = CycleDetector.detect(dependency_map)
        layers = [LayerDetector.classify(path) for path in all_paths]
        contents_by_path = {record['path']: record['content'] for record in file_records if record.get('path')}
        entrypoints = EntrypointDetector.detect(all_paths, contents_by_path)

        summary = {
            'repository_id': str(repo.id),
            'node_count': len(nodes),
            'file_count': len(all_paths),
            'dependency_count': len(edges),
            'cycle_count': len(cycles),
            'layer_count': len({layer.layer_name for layer in layers}),
            'entrypoint_count': len(entrypoints),
            'analysis_version': 'architecture-v1',
        }

        snapshot = ArchitectureSnapshot(
            repository_id=repo.id,
            status='completed',
            analysis_version='architecture-v1',
            summary=json.dumps(summary),
            node_count=len(nodes),
            edge_count=len(edges),
            cycle_count=len(cycles),
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)

        snapshot.nodes_json = json.dumps({node_id: node.to_dict() for node_id, node in nodes.items()})
        snapshot.edges_json = json.dumps(GraphSerializer.serialize_edges(edges))
        snapshot.cycles_json = json.dumps(GraphSerializer.serialize_cycles(cycles))
        snapshot.layers_json = json.dumps(GraphSerializer.serialize_layers(layers))
        snapshot.entrypoints_json = json.dumps(GraphSerializer.serialize_entrypoints(entrypoints))
        db.add(snapshot)
        db.commit()

        impact_samples = {}
        for target in sorted({path for path in all_paths if path}):
            if target in dependency_map or any(target in deps for deps in dependency_map.values()):
                impact_samples[target] = ImpactAnalyzer.analyze(dependency_map, target)

        return {
            'snapshot_id': str(snapshot.id),
            'summary': summary,
            'nodes': GraphSerializer.serialize_nodes(nodes.values()),
            'edges': GraphSerializer.serialize_edges(edges),
            'cycles': GraphSerializer.serialize_cycles(cycles),
            'layers': GraphSerializer.serialize_layers(layers),
            'entrypoints': GraphSerializer.serialize_entrypoints(entrypoints),
            'impact_analysis': impact_samples,
        }

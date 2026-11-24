"""Build the repository directory hierarchy and file graph."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Dict, Iterable, List, Tuple

from app.architecture.models import GraphNode


class GraphBuilder:
    """Build a repository structural graph from file paths."""

    @staticmethod
    def build_hierarchy(repository_id: str, file_paths: Iterable[str]) -> Tuple[Dict[str, GraphNode], Dict[str, List[str]]]:
        nodes: Dict[str, GraphNode] = {}
        adjacency: Dict[str, List[str]] = {}
        root_id = f"repo:{repository_id}:root"
        root = GraphNode(
            node_id=root_id,
            repository_id=repository_id,
            name="repository",
            path=".",
            node_type="root",
            language="repo",
        )
        nodes[root_id] = root
        adjacency[root_id] = []

        seen_dirs: set[str] = set()
        for raw in sorted(set(file_paths)):
            normalized = raw.replace('\\', '/').strip('/');
            if not normalized:
                continue
            path = PurePosixPath(normalized)
            parts = list(path.parts)
            current_id = root_id
            parent_id = root_id
            for index, part in enumerate(parts[:-1]):
                dir_path = '/'.join(parts[: index + 1])
                dir_id = f"dir:{repository_id}:{dir_path}"
                if dir_id not in nodes:
                    nodes[dir_id] = GraphNode(
                        node_id=dir_id,
                        repository_id=repository_id,
                        name=part,
                        path=dir_path,
                        node_type="directory",
                        language="dir",
                        parent_node_id=current_id,
                    )
                    adjacency.setdefault(current_id, []).append(dir_id)
                    adjacency.setdefault(dir_id, [])
                current_id = dir_id
                parent_id = dir_id

            file_name = parts[-1]
            file_id = f"file:{repository_id}:{normalized}"
            suffix = path.suffix.lower()
            language = {
                '.py': 'python',
                '.ts': 'typescript',
                '.tsx': 'typescript',
                '.js': 'javascript',
                '.jsx': 'javascript',
                '.java': 'java',
                '.go': 'go',
                '.rs': 'rust',
                '.cs': 'csharp',
                '.md': 'markdown',
                '.yaml': 'yaml',
                '.yml': 'yaml',
                '.json': 'json',
                '.toml': 'toml',
                '.sql': 'sql',
                '.sh': 'bash',
            }.get(suffix, 'text')
            nodes[file_id] = GraphNode(
                node_id=file_id,
                repository_id=repository_id,
                name=file_name,
                path=normalized,
                node_type='file',
                language=language,
                parent_node_id=current_id,
                metadata={'extension': suffix or '.none'},
            )
            adjacency.setdefault(current_id, []).append(file_id)
            adjacency.setdefault(file_id, [])

        return nodes, adjacency

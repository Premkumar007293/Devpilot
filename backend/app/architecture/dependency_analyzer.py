"""Static dependency extraction for supported repository languages."""

from __future__ import annotations

import ast
import posixpath
import re
from typing import Dict, Iterable, List, Set

from app.architecture.models import GraphEdge
from app.architecture.symbol_analyzer import SymbolAnalyzer


class DependencyAnalyzer:
    """Build dependency edges between repository files and modules using static analysis."""

    @staticmethod
    def _normalize_path(path: str) -> str:
        return path.replace('\\', '/').strip('./')

    @staticmethod
    def _module_to_path(module: str) -> str:
        module = module.strip()
        if module.startswith('.'):
            return module
        if module.startswith('app.') or module.startswith('src.'):
            return module.replace('.', '/') + '.py'
        return module.split('/')[0]

    @staticmethod
    def _python_import_edges(file_path: str, content: str) -> List[GraphEdge]:
        try:
            parsed = ast.parse(content)
        except SyntaxError:
            return []

        edges: List[GraphEdge] = []
        for node in ast.walk(parsed):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    edges.append(
                        GraphEdge(
                            edge_id=f"{file_path}->{alias.name}",
                            source_node=file_path,
                            target_node=alias.name,
                            relationship_type='imports',
                            source_file=file_path,
                            source_line=getattr(node, 'lineno', None),
                            confidence=0.9,
                            detection_method='ast-import',
                            metadata={'import': alias.name},
                        )
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                if module:
                    edges.append(
                        GraphEdge(
                            edge_id=f"{file_path}->{module}",
                            source_node=file_path,
                            target_node=module,
                            relationship_type='imports',
                            source_file=file_path,
                            source_line=getattr(node, 'lineno', None),
                            confidence=0.9,
                            detection_method='ast-import-from',
                            metadata={'module': module, 'level': node.level},
                        )
                    )
        return edges

    @staticmethod
    def _js_import_edges(file_path: str, content: str) -> List[GraphEdge]:
        edges: List[GraphEdge] = []
        patterns = [
            re.compile(r"import\s+(?:.+?\s+from\s+)?['\"]([^'\"]+)['\"]"),
            re.compile(r"require\(['\"]([^'\"]+)['\"]\)"),
            re.compile(r"export\s+\*\s+from\s+['\"]([^'\"]+)['\"]"),
        ]
        for pattern in patterns:
            for match in pattern.finditer(content):
                target = match.group(1)
                if not target:
                    continue
                edges.append(
                    GraphEdge(
                        edge_id=f"{file_path}->{target}",
                        source_node=file_path,
                        target_node=target,
                        relationship_type='imports',
                        source_file=file_path,
                        source_line=content[: match.start()].count('\n') + 1,
                        confidence=0.8,
                        detection_method='regex-import',
                        metadata={'import': target},
                    )
                )
        return edges

    @staticmethod
    def _resolve_relative_import(file_path: str, target: str, file_index: Dict[str, str]) -> str | None:
        if not target.startswith('.'):
            return None
        base_dir = file_path.rsplit('/', 1)[0] if '/' in file_path else ''
        normalized = posixpath.normpath(posixpath.join(base_dir, target))
        candidates = [normalized]
        if not normalized.endswith('.py') and not normalized.endswith(('.ts', '.tsx', '.js', '.jsx')):
            candidates.extend([
                normalized + '.py',
                normalized + '.ts',
                normalized + '.tsx',
                normalized + '.js',
                normalized + '.jsx',
                posixpath.join(normalized, 'index.py'),
                posixpath.join(normalized, 'index.ts'),
                posixpath.join(normalized, 'index.tsx'),
                posixpath.join(normalized, 'index.js'),
                posixpath.join(normalized, 'index.jsx'),
            ])
        for candidate in candidates:
            if candidate in file_index:
                return candidate
        return None

    @staticmethod
    def _resolve_internal_dependencies(file_path: str, edges: List[GraphEdge], file_index: Dict[str, str]) -> List[GraphEdge]:
        result: List[GraphEdge] = []
        for edge in edges:
            target = edge.target_node or ''
            if not target:
                continue
            normalized = None

            if target.startswith('.'):
                normalized = DependencyAnalyzer._resolve_relative_import(file_path, target, file_index)
            elif target in file_index:
                normalized = target
            elif target.replace('./', '') in file_index:
                normalized = target.replace('./', '')
            elif target.startswith('app.') or target.startswith('src.'):
                normalized = DependencyAnalyzer._module_to_path(target)
                if normalized not in file_index:
                    normalized = None
            elif '/' not in target and '.' in target and target.split('.')[-1] in {'py', 'ts', 'tsx', 'js', 'jsx'}:
                normalized = next((candidate for candidate in file_index if candidate.endswith('/' + target)), None)

            if normalized:
                edge.target_node = normalized
                edge.metadata['resolved_path'] = normalized
                edge.confidence = max(edge.confidence, 0.95)
            else:
                edge.metadata['unresolved_target'] = target
            result.append(edge)
        return result

    def analyze(self, files: Iterable[dict]) -> List[GraphEdge]:
        indexed: Dict[str, str] = {}
        file_list = list(files)
        for file in file_list:
            path = str(file.get('path') or file.get('file_path') or '').replace('\\', '/')
            if path:
                indexed[path] = path

        all_edges: List[GraphEdge] = []
        for file in file_list:
            path = str(file.get('path') or file.get('file_path') or '').replace('\\', '/')
            content = str(file.get('content') or '')
            if not path or not content:
                continue
            suffix = path.lower().rsplit('.', 1)[-1] if '.' in path else ''
            if suffix == 'py':
                all_edges.extend(self._python_import_edges(path, content))
                symbol_analysis = SymbolAnalyzer.analyze(path, content)
                all_edges.extend(symbol_analysis.get('edges', []))
            elif suffix in {'js', 'jsx', 'ts', 'tsx'}:
                all_edges.extend(self._js_import_edges(path, content))
                symbol_analysis = SymbolAnalyzer.analyze(path, content)
                all_edges.extend(symbol_analysis.get('edges', []))

        resolved_edges = []
        for edge in all_edges:
            if not edge.target_node:
                continue
            resolved_edges.extend(self._resolve_internal_dependencies(edge.source_file or edge.source_node, [edge], indexed))

        deduped: Dict[str, GraphEdge] = {}
        for edge in resolved_edges:
            deduped.setdefault(edge.edge_id, edge)
        return list(deduped.values())

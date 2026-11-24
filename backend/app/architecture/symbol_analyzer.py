"""Lightweight symbol extraction for Python, TypeScript, and JavaScript source files."""

from __future__ import annotations

import ast
import re
from typing import Any, Dict, List

from app.architecture.models import GraphEdge


class SymbolAnalyzer:
    """Extract classes, functions, and symbol relationships from source text."""

    @staticmethod
    def analyze(file_path: str, content: str) -> Dict[str, List[Any]]:
        suffix = file_path.lower().rsplit('.', 1)[-1] if '.' in file_path else ''
        if suffix == 'py':
            return SymbolAnalyzer._analyze_python(file_path, content)
        if suffix in {'js', 'jsx', 'ts', 'tsx'}:
            return SymbolAnalyzer._analyze_javascript(file_path, content)
        return {'symbols': [], 'edges': []}

    @staticmethod
    def _analyze_python(file_path: str, content: str) -> Dict[str, List[Any]]:
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {'symbols': [], 'edges': []}

        symbols: List[dict] = []
        edges: List[GraphEdge] = []
        class_stack: List[str] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                symbols.append({
                    'name': node.name,
                    'kind': 'class',
                    'file_path': file_path,
                    'line': getattr(node, 'lineno', 0),
                    'parent': class_stack[-1] if class_stack else None,
                })
                for base in node.bases:
                    base_name = getattr(base, 'id', None)
                    if base_name:
                        edges.append(GraphEdge(
                            edge_id=f"{file_path}:{node.name}->{base_name}",
                            source_node=f"{file_path}:{node.name}",
                            target_node=base_name,
                            relationship_type='inherits',
                            source_file=file_path,
                            source_line=getattr(node, 'lineno', None),
                            confidence=0.9,
                            detection_method='ast-class-base',
                            metadata={'symbol': node.name, 'base': base_name},
                        ))
                class_stack.append(node.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                symbols.append({
                    'name': node.name,
                    'kind': 'function',
                    'file_path': file_path,
                    'line': getattr(node, 'lineno', 0),
                    'parent': class_stack[-1] if class_stack else None,
                })
                for child in ast.walk(node):
                    if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                        edges.append(GraphEdge(
                            edge_id=f"{file_path}:{node.name}->{child.func.id}",
                            source_node=f"{file_path}:{node.name}",
                            target_node=child.func.id,
                            relationship_type='calls',
                            source_file=file_path,
                            source_line=getattr(node, 'lineno', None),
                            confidence=0.75,
                            detection_method='ast-call',
                            metadata={'callee': child.func.id},
                        ))

        return {'symbols': symbols, 'edges': edges}

    @staticmethod
    def _analyze_javascript(file_path: str, content: str) -> Dict[str, List[Any]]:
        symbols: List[dict] = []
        edges: List[GraphEdge] = []
        class_pattern = re.compile(r"class\s+(\w+)\s*(?:extends\s+(\w+))?", re.MULTILINE)
        function_pattern = re.compile(r"(?:function\s+(\w+)\s*\(|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>)", re.MULTILINE)

        for match in class_pattern.finditer(content):
            class_name = match.group(1)
            parent_name = match.group(2)
            symbols.append({'name': class_name, 'kind': 'class', 'file_path': file_path, 'line': content[:match.start()].count('\n') + 1})
            if parent_name:
                edges.append(GraphEdge(
                    edge_id=f"{file_path}:{class_name}->{parent_name}",
                    source_node=f"{file_path}:{class_name}",
                    target_node=parent_name,
                    relationship_type='inherits',
                    source_file=file_path,
                    source_line=content[:match.start()].count('\n') + 1,
                    confidence=0.8,
                    detection_method='regex-class-extends',
                    metadata={'class': class_name, 'parent': parent_name},
                ))

        for match in function_pattern.finditer(content):
            name = next(group for group in match.groups() if group)
            symbols.append({'name': name, 'kind': 'function', 'file_path': file_path, 'line': content[:match.start()].count('\n') + 1})

        return {'symbols': symbols, 'edges': edges}

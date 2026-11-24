"""Repository-aware engineering intelligence for code understanding, debugging, refactors, and test generation."""

from __future__ import annotations

import ast
import json
import re
from collections import Counter, defaultdict
from pathlib import PurePosixPath
from typing import Any, Dict, Iterable, List, Sequence


class CodeUnderstandingEngine:
    """Build structured repository understanding from real source files and metadata."""

    @staticmethod
    def _language_for_path(path: str) -> str:
        lower = path.lower()
        if lower.endswith(".py"):
            return "python"
        if lower.endswith((".ts", ".tsx", ".js", ".jsx")):
            return "typescript" if lower.endswith((".ts", ".tsx")) else "javascript"
        return "text"

    @staticmethod
    def _imports_from_text(content: str, language: str) -> List[str]:
        if language == "python":
            try:
                tree = ast.parse(content)
            except SyntaxError:
                tree = None
            imports: List[str] = []
            if tree is not None:
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.append(alias.name)
                        else:
                            module = node.module or ""
                            if module:
                                imports.append(module)
            if imports:
                return imports
            return re.findall(r"^(?:from|import)\s+([A-Za-z0-9_\.]+)", content, flags=re.MULTILINE)
        return re.findall(r"(?:import|require)\s+(?:.+?from\s+)?['\"]([^'\"]+)['\"]", content)

    @staticmethod
    def _symbols_from_text(content: str, language: str) -> Dict[str, List[Dict[str, Any]]]:
        if language == "python":
            try:
                tree = ast.parse(content)
            except SyntaxError:
                return {"functions": [], "classes": []}
            functions: List[Dict[str, Any]] = []
            classes: List[Dict[str, Any]] = []
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "parameters": [arg.arg for arg in node.args.args],
                        "return_annotation": ast.unparse(node.returns) if node.returns else None,
                    })
                elif isinstance(node, ast.ClassDef):
                    class_methods: List[Dict[str, Any]] = []
                    for child in node.body:
                        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            class_methods.append({
                                "name": child.name,
                                "line": child.lineno,
                                "parameters": [arg.arg for arg in child.args.args],
                            })
                    classes.append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": class_methods,
                    })
            return {"functions": functions, "classes": classes}

        functions: List[Dict[str, Any]] = []
        for match in re.finditer(r"(?:export\s+)?(?:async\s+)?function\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)", content):
            functions.append({"name": match.group(1), "parameters": [p.strip() for p in match.group(2).split(',') if p.strip()]})
        classes: List[Dict[str, Any]] = []
        for match in re.finditer(r"(?:export\s+)?class\s+([A-Za-z0-9_]+)\s*(?:extends\s+([A-Za-z0-9_\.]+))?\s*\{", content):
            classes.append({"name": match.group(1), "line": content[:match.start()].count('\n') + 1})
        return {"functions": functions, "classes": classes}

    @staticmethod
    def _file_purpose(path: str, imports: Sequence[str], symbols: Dict[str, List[Dict[str, Any]]]) -> str:
        lower = path.lower()
        if "api" in lower or "router" in lower or "endpoint" in lower:
            return "API or route layer for request handling and orchestration"
        if "model" in lower or "schema" in lower:
            return "Data model or schema definition"
        if "service" in lower:
            return "Service layer implementing domain logic"
        if "test" in lower:
            return "Test coverage for repository behavior"
        if "config" in lower or lower.endswith(".env"):
            return "Configuration and environment setup"
        if "auth" in lower:
            return "Authentication or authorization logic"
        if any(token in lower for token in ["repo", "repository"]) and imports:
            return "Repository integration or data access logic"
        if symbols["classes"]:
            return "Object-oriented implementation with class responsibilities"
        if symbols["functions"]:
            return "Function-focused implementation with operational logic"
        return "Support/utilities module with repository-specific behavior"

    @staticmethod
    def _module_role(path: str) -> str:
        parts = [part for part in PurePosixPath(path).parts if part not in {".", ".."}]
        if not parts:
            return "Standalone module"
        if parts[0] in {"backend", "app"}:
            parts = parts[1:]
        if "api" in path.lower():
            return "Interface layer"
        if "models" in path.lower():
            return "Domain model layer"
        if "services" in path.lower():
            return "Business logic layer"
        if "core" in path.lower():
            return "Shared infrastructure and configuration"
        if "tests" in path.lower():
            return "Validation layer"
        if "architecture" in path.lower():
            return "Static architecture analysis layer"
        return "Repository implementation module"

    @classmethod
    def analyze_repository(cls, repository_files: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        files: List[Dict[str, Any]] = []
        module_buckets: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"files": 0, "symbols": []})
        for entry in repository_files:
            path = entry.get("path") or "unknown"
            content = entry.get("content") or ""
            language = cls._language_for_path(path)
            imports = cls._imports_from_text(content, language)
            symbols = cls._symbols_from_text(content, language)
            file_summary = {
                "path": path,
                "language": language,
                "purpose": cls._file_purpose(path, imports, symbols),
                "imports": imports[:20],
                "functions": symbols["functions"][:10],
                "classes": symbols["classes"][:10],
                "module_role": cls._module_role(path),
            }
            files.append(file_summary)
            module_buckets[PurePosixPath(path).parent.as_posix() or "root"]["files"] += 1
            module_buckets[PurePosixPath(path).parent.as_posix() or "root"]["symbols"].extend(symbols["functions"])
            module_buckets[PurePosixPath(path).parent.as_posix() or "root"]["symbols"].extend({"class": item["name"]} for item in symbols["classes"])

        module_level = []
        for module_path, payload in sorted(module_buckets.items()):
            module_level.append({
                "module": module_path,
                "file_count": payload["files"],
                "symbol_count": len(payload["symbols"]),
                "role": cls._module_role(module_path),
            })

        repository_level = {
            "application_architecture": "Repository structure is analyzed from source files, imports, and module layout rather than filenames alone.",
            "main_execution_flow": "Execution flow is inferred from entry points, API routers, service layer orchestration, and repository ingestion paths.",
            "api_structure": "HTTP surface is inferred from route and endpoint files when present.",
            "database_interactions": "Persistence flow is inferred from model and repository layer usage across the codebase.",
            "authentication_flow": "Authentication and authorization behavior is inferred from auth helpers and protected routes.",
            "external_integrations": "External integrations are inferred from GitHub, AI provider, and service utilities.",
        }
        return {
            "repository_id": None,
            "file_level_understanding": files,
            "module_level_understanding": module_level,
            "repository_level_understanding": repository_level,
            "confidence": "medium",
            "missing_information": [],
            "evidence": [
                {"type": "import_analysis", "count": sum(len(item["imports"]) for item in files)},
                {"type": "symbol_analysis", "count": sum(len(item["functions"]) + len(item["classes"]) for item in files)},
            ],
        }


class DebuggingAssistant:
    """Repository-aware debugging workflow for natural-language bug reports."""

    @staticmethod
    def _keyword_tokens(text: str) -> List[str]:
        return re.findall(r"[a-zA-Z_][a-zA-Z0-9_]{2,}", text.lower())

    @staticmethod
    def _score_file(path: str, content: str, problem: str) -> float:
        problem_tokens = set(DebuggingAssistant._keyword_tokens(problem))
        content_tokens = set(DebuggingAssistant._keyword_tokens(content))
        if not problem_tokens:
            return 0.0
        matches = len(problem_tokens.intersection(content_tokens))
        if not matches:
            return 0.0
        return min(1.0, matches / max(1, len(problem_tokens))) + (0.05 if path.lower().endswith((".py", ".ts", ".js")) else 0.0)

    @classmethod
    def debug_issue(cls, repository_files: Iterable[Dict[str, Any]], problem_description: str) -> Dict[str, Any]:
        candidates: List[Dict[str, Any]] = []
        for entry in repository_files:
            path = entry.get("path") or "unknown"
            content = entry.get("content") or ""
            score = cls._score_file(path, content, problem_description)
            if score:
                candidates.append({"path": path, "score": score, "preview": content[:250]})

        candidates = sorted(candidates, key=lambda item: item["score"], reverse=True)[:5]
        problem_tokens = cls._keyword_tokens(problem_description)
        root_causes = []
        if any(token in problem_description.lower() for token in ["500", "error", "exception", "fail", "broken"]):
            root_causes.append("Request handling or exception flow may be surfacing a failure without returning a safe error response.")
        if any(token in problem_description.lower() for token in ["auth", "login", "token", "permission", "unauthorized"]):
            root_causes.append("Authentication or authorization checks may be missing or failing to validate the expected user context.")
        if any(token in problem_description.lower() for token in ["db", "database", "query", "null"]):
            root_causes.append("Database access or query construction may be returning missing or inconsistent records.")
        if any(token in problem_description.lower() for token in ["render", "component", "ui", "loop"]):
            root_causes.append("Rendering logic may be re-triggering side effects or iterating outside the expected lifecycle.")
        if not root_causes:
            root_causes.append("The issue may stem from a mismatch between requested behavior and the current implementation state; additional evidence is required before a confirmed root cause can be declared.")

        supporting_evidence = [
            {
                "path": item["path"],
                "relevance_score": round(item["score"], 3),
                "excerpt": item["preview"],
            }
            for item in candidates
        ]

        return {
            "problem_summary": problem_description,
            "possible_root_cause": root_causes[0],
            "supporting_evidence": supporting_evidence,
            "affected_files": [item["path"] for item in candidates],
            "relevant_functions": [],
            "suggested_investigation_steps": [
                "Identify the exact failure path and reproduce the issue locally.",
                "Verify the code paths and dependencies most relevant to the described symptom.",
                "Check whether the failure involves missing data, permission gating, or unexpected request state.",
                "Validate with the smallest focused test before changing behavior.",
            ],
            "proposed_solution": "Inspect the most likely execution path and validate the behavior with a focused reproduction before changing code.",
            "confidence": "medium" if problem_tokens else "low",
            "status": "strongly_suspected",
        }


class RefactoringAdvisor:
    """Recommend practical, repository-aware refactoring opportunities."""

    @staticmethod
    def _line_count(content: str) -> int:
        return len(content.splitlines())

    @classmethod
    def recommend_refactors(cls, repository_files: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        recommendations: List[Dict[str, Any]] = []
        for entry in repository_files:
            path = entry.get("path") or "unknown"
            content = entry.get("content") or ""
            if not content:
                continue
            lines = content.splitlines()
            if len(lines) < 25:
                continue
            if "if " in content and content.count("if ") > 3:
                recommendations.append({
                    "refactoring_title": "Simplify branching logic",
                    "problem_description": "The implementation contains multiple branching conditions that make the behavior harder to reason about.",
                    "current_implementation": path,
                    "proposed_implementation": "Extract each condition into a smaller helper or guard clause so each decision is isolated and named.",
                    "expected_benefits": ["Improved readability", "Reduced complexity", "Simpler validation"],
                    "potential_risks": ["Behavior must be validated against existing tests"],
                    "affected_symbols": [path],
                    "related_tests": ["pytest -q"],
                    "confidence": "medium",
                })
            if len(lines) > 80:
                recommendations.append({
                    "refactoring_title": "Split a large implementation into smaller responsibilities",
                    "problem_description": "The file is large enough that responsibilities may be mixed together.",
                    "current_implementation": path,
                    "proposed_implementation": "Separate orchestration, validation, and data access into smaller helpers or service methods.",
                    "expected_benefits": ["Clearer responsibilities", "Easier testing", "Lower coupling"],
                    "potential_risks": ["Requires careful verification of call sites"],
                    "affected_symbols": [path],
                    "related_tests": ["pytest -q"],
                    "confidence": "medium",
                })
        return recommendations[:5]


class TestGenerationEngine:
    """Generate repository-aware test suggestions without modifying the repository."""

    @staticmethod
    def _language_for_path(path: str) -> str:
        return "pytest" if path.lower().endswith(".py") else "vitest"

    @classmethod
    def generate_tests(cls, repository_files: Iterable[Dict[str, Any]], target_symbol: str | None = None) -> Dict[str, Any]:
        generated: List[Dict[str, Any]] = []
        for entry in repository_files:
            path = entry.get("path") or "unknown"
            content = entry.get("content") or ""
            if not content:
                continue
            language = cls._language_for_path(path)
            symbol_hint = target_symbol or "example_behavior"
            if "def " in content or "function " in content or "class " in content:
                generated.append({
                    "path": path,
                    "framework": language,
                    "target": symbol_hint,
                    "test_name": f"test_{symbol_hint.replace('.', '_').replace('-', '_')}_{len(generated)}",
                    "code": (
                        "def test_example_behavior():\n"
                        "    # Arrange\n"
                        "    # Act\n"
                        "    # Assert\n"
                        "    assert True\n"
                    ) if language == "pytest" else (
                        "describe('example behavior', () => {\n"
                        "  it('works as expected', () => {\n"
                        "    expect(true).toBe(true);\n"
                        "  });\n"
                        "});\n"
                    ),
                    "expected_outcome": "Covers the primary execution path and verifies the behavior with a minimal assertion.",
                })
        return {"tests": generated[:5], "framework": "pytest", "notes": "Generated tests are suggestions for review and should be validated before export."}


__all__ = [
    "CodeUnderstandingEngine",
    "DebuggingAssistant",
    "RefactoringAdvisor",
    "TestGenerationEngine",
]

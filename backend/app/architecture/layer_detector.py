"""Heuristic architectural layer detection for repository files."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Dict, Iterable, List

from app.architecture.models import ArchitectureLayer


class LayerDetector:
    """Classify files and modules into likely architecture layers."""

    @staticmethod
    def classify(path: str) -> ArchitectureLayer:
        normalized = path.replace('\\', '/')
        lower = normalized.lower()
        evidence: List[str] = []

        if '/api/' in lower or lower.endswith('/routes.py') or lower.endswith('/router.py'):
            evidence.append('api directory or router naming')
            return ArchitectureLayer(file_path=normalized, layer_name='API', confidence=0.9, evidence=evidence)
        if '/routes/' in lower or '/controllers/' in lower or lower.endswith('/controller.py'):
            evidence.append('route/controller naming')
            return ArchitectureLayer(file_path=normalized, layer_name='Controllers', confidence=0.8, evidence=evidence)
        if '/services/' in lower or lower.endswith('/service.py') or 'service' in lower:
            evidence.append('service naming')
            return ArchitectureLayer(file_path=normalized, layer_name='Services', confidence=0.9, evidence=evidence)
        if '/models/' in lower or lower.endswith('/model.py') or 'model' in lower:
            evidence.append('model naming')
            return ArchitectureLayer(file_path=normalized, layer_name='Models', confidence=0.9, evidence=evidence)
        if '/database/' in lower or 'db' in lower or 'repository' in lower:
            evidence.append('database/data access naming')
            return ArchitectureLayer(file_path=normalized, layer_name='Data Access', confidence=0.8, evidence=evidence)
        if '/tests/' in lower or lower.startswith('tests/') or lower.endswith('_test.py') or 'test_' in lower:
            evidence.append('test naming')
            return ArchitectureLayer(file_path=normalized, layer_name='Tests', confidence=0.95, evidence=evidence)
        if '/config/' in lower or lower.endswith('settings.py') or 'config' in lower:
            evidence.append('configuration naming')
            return ArchitectureLayer(file_path=normalized, layer_name='Configuration', confidence=0.8, evidence=evidence)
        if '/security/' in lower or 'auth' in lower or 'security' in lower:
            evidence.append('security/auth naming')
            return ArchitectureLayer(file_path=normalized, layer_name='Security', confidence=0.85, evidence=evidence)
        if '/utils/' in lower or 'util' in lower or lower.endswith('/helpers.py'):
            evidence.append('utility naming')
            return ArchitectureLayer(file_path=normalized, layer_name='Utilities', confidence=0.7, evidence=evidence)

        return ArchitectureLayer(file_path=normalized, layer_name='Business Logic', confidence=0.6, evidence=['folder and file naming did not match stronger signals'])

    def classify_many(self, paths: Iterable[str]) -> List[ArchitectureLayer]:
        return [self.classify(path) for path in paths]

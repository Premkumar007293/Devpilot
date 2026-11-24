"""Detect application entry points from repository conventions."""

from __future__ import annotations

from typing import Iterable, List

from app.architecture.models import EntryPoint


class EntrypointDetector:
    """Identify likely application entry points from file names and startup patterns."""

    @staticmethod
    def detect(paths: Iterable[str], contents: dict[str, str]) -> List[EntryPoint]:
        entrypoints: List[EntryPoint] = []
        for path in sorted(set(paths)):
            lower = path.lower().replace('\\', '/')
            content = contents.get(path, '')
            if lower.endswith('main.py') or lower.endswith('app.py') or lower.endswith('server.py'):
                evidence = ['common application startup filename']
                if 'FastAPI' in content or 'Flask' in content or 'app = ' in content:
                    evidence.append('application factory or server bootstrap detected')
                entrypoints.append(EntryPoint(file_path=path, symbol_name='main', entry_type='application', detection_evidence=evidence))
            elif lower.endswith('index.ts') or lower.endswith('index.tsx') or lower.endswith('main.ts') or lower.endswith('main.tsx'):
                evidence = ['frontend entry file naming']
                if 'ReactDOM' in content or 'createRoot' in content:
                    evidence.append('React bootstrap detected')
                entrypoints.append(EntryPoint(file_path=path, symbol_name='index', entry_type='frontend', detection_evidence=evidence))
            elif lower.endswith('manage.py'):
                entrypoints.append(EntryPoint(file_path=path, symbol_name='main', entry_type='cli', detection_evidence=['Django management entrypoint naming']))
        return entrypoints

"""Architecture engine smoke tests for repository dependency analysis."""

from app.architecture.cycle_detector import CycleDetector
from app.architecture.dependency_analyzer import DependencyAnalyzer
from app.architecture.impact_analyzer import ImpactAnalyzer


def test_dependency_analyzer_resolves_internal_python_imports():
    files = [
        {"path": "app/main.py", "content": "from app.utils import helper\n\nhelper()\n"},
        {"path": "app/utils.py", "content": "def helper():\n    return 42\n"},
    ]

    edges = DependencyAnalyzer().analyze(files)
    targets = {edge.target_node for edge in edges}
    assert any(target.endswith("utils.py") for target in targets)


def test_cycle_detector_identifies_circular_dependency():
    graph = {
        "alpha": ["beta"],
        "beta": ["gamma"],
        "gamma": ["alpha"],
        "delta": ["epsilon"],
    }

    cycles = CycleDetector.detect(graph)
    assert len(cycles) == 1
    assert set(cycles[0].participants) == {"alpha", "beta", "gamma"}


def test_impact_analyzer_reports_direct_and_transitive_dependents():
    graph = {
        "core.py": ["util.py"],
        "service.py": ["core.py"],
        "api.py": ["service.py"],
    }

    impact = ImpactAnalyzer.analyze(graph, "core.py")
    assert impact["target"] == "core.py"
    assert "service.py" in impact["direct_dependents"]
    assert "api.py" in impact["transitive_dependents"]

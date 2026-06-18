"""Artifact path resolution tests."""

from pathlib import Path

from qspecbench.validate import validate_path

REPO = Path(__file__).resolve().parents[1]


def test_full_benchmarks_validate():
    results = validate_path(REPO / "benchmarks")
    failures = [r for r in results if not r.ok]
    assert not failures, "\n".join(f"{r.spec_path}: {r.errors}" for r in failures)

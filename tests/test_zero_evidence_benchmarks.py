"""Ensure every benchmark declares at least one evidence entry."""

from pathlib import Path

from qspecbench.artifacts import find_spec_files
from qspecbench.validate import load_spec

REPO = Path(__file__).resolve().parents[1]


def test_no_zero_evidence_benchmarks():
    missing = []
    for spec_path in find_spec_files(REPO / "benchmarks"):
        spec = load_spec(spec_path)
        if not spec.get("evidence"):
            missing.append(spec_path.parent.name)
    assert not missing, f"benchmarks with evidence: []: {', '.join(sorted(missing))}"

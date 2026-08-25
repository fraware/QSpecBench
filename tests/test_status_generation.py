"""Status generation tests."""

from pathlib import Path

from qspecbench.dashboard import zero_evidence_count
from qspecbench.models import ARTIFACT_BOUND_LEVEL, REFERENCE_CLAIM_LEVEL, REFERENCE_SCAFFOLD_LEVELS
from qspecbench.status import collect_statuses

REPO = Path(__file__).resolve().parents[1]


def test_collect_statuses_nonempty():
    rows = collect_statuses(REPO / "benchmarks")
    assert len(rows) >= 48
    assert all(r["id"] for r in rows)


def test_usable_benchmarks_exist():
    rows = collect_statuses(REPO / "benchmarks")
    usable = [r for r in rows if r["maturity"] == "usable"]
    scaffolds = [r for r in rows if r["maturity"] in REFERENCE_SCAFFOLD_LEVELS]
    gold = [r for r in rows if r["maturity"] in {REFERENCE_CLAIM_LEVEL, ARTIFACT_BOUND_LEVEL}]
    experimental = [r for r in rows if r["maturity"] == "experimental_closed"]
    assert len(usable) + len(scaffolds) + len(gold) + len(experimental) >= 35
    assert len(gold) == 0
    assert len(experimental) >= 19


def test_zero_evidence_count_is_zero():
    assert zero_evidence_count(REPO / "benchmarks") == 0

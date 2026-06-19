"""Status generation tests."""

from pathlib import Path

from qspecbench.dashboard import zero_evidence_count
from qspecbench.status import collect_statuses

REPO = Path(__file__).resolve().parents[1]


def test_collect_statuses_nonempty():
    rows = collect_statuses(REPO / "benchmarks")
    assert len(rows) >= 48
    assert all(r["id"] for r in rows)


def test_usable_benchmarks_exist():
    rows = collect_statuses(REPO / "benchmarks")
    usable = [r for r in rows if r["maturity"] == "usable"]
    reference = [r for r in rows if r["maturity"] == "reference"]
    assert len(usable) + len(reference) >= 35
    assert len(reference) >= 8


def test_zero_evidence_count_is_zero():
    assert zero_evidence_count(REPO / "benchmarks") == 0

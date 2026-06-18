"""Status generation tests."""

from pathlib import Path

from qspecbench.status import collect_statuses

REPO = Path(__file__).resolve().parents[1]


def test_collect_statuses_nonempty():
    rows = collect_statuses(REPO / "benchmarks")
    assert len(rows) >= 34
    assert all(r["id"] for r in rows)


def test_usable_benchmarks_exist():
    rows = collect_statuses(REPO / "benchmarks")
    usable = [r for r in rows if r["maturity"] == "usable"]
    reference = [r for r in rows if r["maturity"] == "reference"]
    assert len(usable) >= 10
    assert len(usable) + len(reference) >= 5
    assert len(reference) >= 1

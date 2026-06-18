"""Benchmark layout tests."""

from pathlib import Path

from qspecbench.artifacts import check_layout, find_spec_files

REPO = Path(__file__).resolve().parents[1]


def test_all_benchmarks_have_required_dirs():
    for spec in find_spec_files(REPO / "benchmarks"):
        claim_dir = spec.parent
        errors = check_layout(claim_dir)
        assert not errors, f"{claim_dir}: {errors}"


def test_minimum_corpus_size():
    specs = find_spec_files(REPO / "benchmarks")
    assert len(specs) >= 34

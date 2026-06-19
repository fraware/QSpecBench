"""Benchmark layout tests."""

from pathlib import Path

import yaml

from qspecbench.artifacts import check_layout, find_spec_files, track_for_claim
from qspecbench.validate import validate_spec_dict

REPO = Path(__file__).resolve().parents[1]

TRACK_MAP = {
    "algorithms": "algorithm",
    "equivalence": "equivalence",
    "qec": "qec",
    "hamiltonian": "hamiltonian",
    "ai_formalization": "ai_formalization",
}


def test_all_benchmarks_have_required_dirs():
    for spec in find_spec_files(REPO / "benchmarks"):
        claim_dir = spec.parent
        errors = check_layout(claim_dir)
        assert not errors, f"{claim_dir}: {errors}"


def test_minimum_corpus_size():
    specs = find_spec_files(REPO / "benchmarks")
    assert len(specs) >= 34


def test_track_matches_parent_directory():
    benchmarks_root = REPO / "benchmarks"
    for spec_path in find_spec_files(benchmarks_root):
        spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        claim_dir = spec_path.parent
        track = track_for_claim(claim_dir, benchmarks_root)
        expected = TRACK_MAP.get(track)
        assert expected, f"unknown track directory {track}"
        assert spec.get("track") == expected, f"{spec['id']}: track mismatch"


def test_deprecated_readme_must_explain():
    benchmarks_root = REPO / "benchmarks"
    for spec_path in find_spec_files(benchmarks_root):
        spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        if spec.get("status", {}).get("maturity") != "deprecated":
            continue
        errors, _warnings = validate_spec_dict(spec, spec_path.parent, benchmarks_root)
        assert not any("deprecated benchmark README" in e for e in errors)

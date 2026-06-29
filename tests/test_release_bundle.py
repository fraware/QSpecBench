"""Tests for release bundle CLI."""

from __future__ import annotations

import json
import tarfile
from pathlib import Path

import yaml

from qspecbench.release_bundle import collect_release_manifest, verify_release_bundle, write_release_bundle

REPO = Path(__file__).resolve().parents[1]


def test_release_bundle_contains_manifest_and_schemas(tmp_path):
    out = tmp_path / "bundle.tar.gz"
    manifest = write_release_bundle(REPO / "benchmarks", out)
    assert manifest["benchmark_count"] >= 40
    assert manifest["reproducibility"]["tooling_version"]
    assert manifest.get("bundle_manifest_sha256")
    assert len(manifest["bundle_manifest_sha256"]) == 64
    assert out.is_file()

    with tarfile.open(out, "r:gz") as tar:
        names = tar.getnames()
    assert "manifest.json" in names
    assert "reproducibility.json" in names
    assert any(n.startswith("schema/") and n.endswith(".json") for n in names)
    assert any(n.endswith("/spec.yaml") for n in names)
    assert any("/artifacts/" in n for n in names)


def test_release_manifest_summary_matches_dashboard():
    metrics = collect_release_manifest(REPO / "benchmarks")["summary"]
    assert metrics["total_benchmarks"] >= 40
    assert "reference_claim" in metrics
    assert "manifest_checked_theorem_binding" in metrics


def test_release_bundle_includes_provenance_from_spec(tmp_path):
    claim = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation"
    out = tmp_path / "bundle.tar.gz"
    write_release_bundle(REPO / "benchmarks", out)
    arc_suffix = "cnot_self_inverse_cancellation/provenance.from_spec.json"
    with tarfile.open(out, "r:gz") as tar:
        match = next(n for n in tar.getnames() if n.replace("\\", "/").endswith(arc_suffix))
        data = json.loads(tar.extractfile(match).read().decode("utf-8"))
    spec = yaml.safe_load((claim / "spec.yaml").read_text(encoding="utf-8"))
    assert data == spec["provenance"]


def test_verify_release_bundle_passes(tmp_path):
    out = tmp_path / "bundle.tar.gz"
    manifest = write_release_bundle(REPO / "benchmarks", out)
    assert manifest.get("bundle_files")
    assert manifest.get("bundle_file_count", 0) >= 10
    assert verify_release_bundle(out) == []


def test_release_manifest_accepts_explicit_ci_run_metadata():
    manifest = collect_release_manifest(
        REPO / "benchmarks",
        ci_run_id="123456789",
        ci_run_url="https://github.com/example/actions/runs/123456789",
    )
    repro = manifest["reproducibility"]
    assert repro["ci_run_id"] == "123456789"
    assert repro["ci_run_url"] == "https://github.com/example/actions/runs/123456789"


def test_release_manifest_includes_git_commit():
    manifest = collect_release_manifest(REPO / "benchmarks")
    assert manifest["reproducibility"].get("git_commit")


def test_release_manifest_includes_sbom_summary():
    manifest = collect_release_manifest(REPO / "benchmarks")
    sbom = manifest.get("sbom_summary") or {}
    assert sbom.get("format") == "qspecbench-sbom-lite-v0.1"
    assert sbom.get("python_dependencies")
    assert sbom.get("lean_requires")


def test_verify_release_bundle_integration_sample(tmp_path):
    """Full verify on a corpus-sized bundle (manifest + file hashes + repro fields)."""
    out = tmp_path / "bundle.tar.gz"
    manifest = write_release_bundle(REPO / "benchmarks", out)
    repro = manifest["reproducibility"]
    assert repro.get("schema_version")
    assert repro.get("git_commit")
    assert manifest.get("sbom_summary")
    assert manifest["benchmark_count"] == len(manifest["benchmarks"])
    with tarfile.open(out, "r:gz") as tar:
        names = {n.replace("\\", "/") for n in tar.getnames()}
        assert "schema/bridge_theorem_manifest.json" in names
    errors = verify_release_bundle(out)
    assert errors == [], f"verify failed: {errors}"

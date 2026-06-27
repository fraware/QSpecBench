"""Lean kernel evidence tests (skipped when lake is unavailable)."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from qspecbench.evidence_runner import run_evidence_checks

REPO = Path(__file__).resolve().parents[1]
HAS_LAKE = shutil.which("lake") is not None or (Path.home() / ".elan" / "bin" / "lake").is_file()

pytestmark = pytest.mark.skipif(not HAS_LAKE, reason="Lean 4 / lake not installed")


def test_lean_cnot_proof_passes():
    claim = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation"
    results = {r.evidence_id: r for r in run_evidence_checks(claim)}
    assert "lean_cnot_proof" in results
    assert results["lean_cnot_proof"].ok, results["lean_cnot_proof"].errors


def test_reference_has_passing_lean_proof():
    import yaml

    spec = yaml.safe_load(
        (REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation/spec.yaml").read_text(encoding="utf-8")
    )
    assert spec["status"]["maturity"] == "reference_scaffold"
    lean = [e for e in spec["evidence"] if e["type"] == "lean_proof" and e["status"] == "passing"]
    assert len(lean) >= 1

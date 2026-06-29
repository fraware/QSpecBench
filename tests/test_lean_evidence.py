"""Tests for Lean evidence adapter (direct compile)."""

from __future__ import annotations

import shutil
import tempfile
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


def test_lean_cnot_evidence_compiles_standalone():
    from adapters.lean.parse_result import check

    evidence = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation/evidence/cnot_self_inverse.lean"
    result = check(evidence)
    assert result["ok"], result.get("errors", [])


def test_lean_nonexistent_theorem_fails():
    from adapters.lean.parse_result import check

    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "bad_evidence.lean"
        bad.write_text(
            "import QSpecBench.Quantum.OpenQASM3\n\n"
            "#check QSpecBench.Quantum.OpenQASM3.nonexistent_theorem\n",
            encoding="utf-8",
        )
        result = check(bad)
        assert not result["ok"]
        assert any("lake env lean failed" in e for e in result.get("errors", []))


def test_lean_missing_import_for_check_fails():
    from adapters.lean.parse_result import check

    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "no_import.lean"
        bad.write_text(
            "#check QSpecBench.Quantum.OpenQASM3.bridge_cnot_codegen_self_inverse\n",
            encoding="utf-8",
        )
        result = check(bad)
        assert not result["ok"]
        assert any("must import" in e for e in result.get("errors", []))


def test_reference_has_passing_lean_proof():
    import yaml

    spec = yaml.safe_load(
        (REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation/spec.yaml").read_text(encoding="utf-8")
    )
    assert spec["status"]["maturity"] == "reference_claim"
    lean = [e for e in spec["evidence"] if e["type"] == "lean_proof" and e["status"] == "passing"]
    assert len(lean) >= 1


def test_scan_lean_package_for_sorry_clean():
    from adapters.lean.parse_result import scan_lean_package_for_sorry

    assert scan_lean_package_for_sorry() == []


def test_lean_adapter_fails_when_package_contains_sorry(tmp_path, monkeypatch):
    from adapters.lean import parse_result

    sorry_file = tmp_path / "SorryModule.lean"
    sorry_file.write_text("theorem bad : True := sorry\n", encoding="utf-8")
    monkeypatch.setattr(parse_result, "scan_lean_package_for_sorry", lambda root=None: ["QSpecBench/SorryModule.lean"])

    evidence = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation/evidence/cnot_self_inverse.lean"
    result = parse_result.check(evidence)
    assert not result["ok"]
    assert any("sorry found in lean package" in e for e in result.get("errors", []))

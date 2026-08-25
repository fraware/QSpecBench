"""Phase F audit gaps: seed QEC, Hamiltonian Lean e2e, dynamic-simulate CLI (F-057–F-059)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from qspecbench.cli import app
from qspecbench.evidence_runner import run_evidence_checks
from qspecbench.validate import load_spec

REPO = Path(__file__).resolve().parents[1]
SEED_QEC = REPO / "benchmarks/qec/repeated_round_qec_temporal_specification"
HAMILTONIAN = REPO / "benchmarks/hamiltonian/small_fermionic_hamiltonian_is_hermitian"
TELEPORT = REPO / "benchmarks/algorithms/teleportation_preserves_state_up_to_pauli_correction"
HAS_LAKE = shutil.which("lake") is not None or (Path.home() / ".elan" / "bin" / "lake").is_file()


def test_seed_qec_repeated_round_layout_and_non_lean_evidence():
    """F-057: sole seed QEC claim stays schema-honest and runnable."""
    spec = load_spec(SEED_QEC / "spec.yaml")
    assert spec["id"] == "repeated_round_qec_temporal_specification"
    assert spec["status"]["maturity"] == "seed"
    assert (SEED_QEC / "artifacts/code.json").is_file()
    assert any(e.get("type") == "qec_verifier_result" for e in spec.get("evidence", []))

    results = {r.evidence_id: r for r in run_evidence_checks(SEED_QEC)}
    assert "code_json_valid" in results
    assert results["code_json_valid"].ok, results["code_json_valid"].errors


@pytest.mark.lean
@pytest.mark.skipif(not HAS_LAKE, reason="Lean 4 / lake not installed")
def test_seed_qec_lean_stabilizer_scaffold_passes():
    """F-057: seed Lean scaffold remains kernel-checkable when lake is present."""
    results = {r.evidence_id: r for r in run_evidence_checks(SEED_QEC)}
    assert "lean_stabilizer_commutation" in results
    assert results["lean_stabilizer_commutation"].ok, results["lean_stabilizer_commutation"].errors


@pytest.mark.lean
@pytest.mark.skipif(not HAS_LAKE, reason="Lean 4 / lake not installed")
def test_hamiltonian_lean_evidence_end_to_end():
    """F-058: Hamiltonian track Lean evidence passes through the runner."""
    spec = yaml.safe_load((HAMILTONIAN / "spec.yaml").read_text(encoding="utf-8"))
    assert spec["status"]["maturity"] == "experimental_closed"
    lean = [e for e in spec["evidence"] if e["type"] == "lean_proof" and e["status"] == "passing"]
    assert len(lean) >= 1

    results = {r.evidence_id: r for r in run_evidence_checks(HAMILTONIAN)}
    assert "lean_hermitian" in results
    assert results["lean_hermitian"].ok, results["lean_hermitian"].errors

    from adapters.lean.parse_result import check

    evidence = HAMILTONIAN / "evidence" / "hermitian.lean"
    direct = check(evidence)
    assert direct["ok"], direct.get("errors", [])


def test_dynamic_simulate_cli_teleport_basis_check(tmp_path):
    """F-059: dynamic-simulate CLI covered by pytest (not CI-only)."""
    out = tmp_path / "dynamic_simulation_basis_check.json"
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "dynamic-simulate",
            str(TELEPORT),
            "--teleport-basis-check",
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.stdout + result.stderr
    assert out.is_file()
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report.get("all_ok") is True
    assert report.get("type") == "teleportation_basis_check_v0"
    assert report.get("input_fingerprint")
    assert len(report.get("results") or []) == 2

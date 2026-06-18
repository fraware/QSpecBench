"""Tests for evidence check runner."""

from pathlib import Path

from qspecbench.evidence_runner import run_evidence_checks

REPO = Path(__file__).resolve().parents[1]


def test_check_evidence_teleportation_qasm():
    claim = REPO / "benchmarks/algorithms/teleportation_preserves_state_up_to_pauli_correction"
    results = [r for r in run_evidence_checks(claim) if not r.skipped]
    assert any(r.ok for r in results)


def test_check_evidence_hermitian_simulation():
    claim = REPO / "benchmarks/hamiltonian/small_fermionic_hamiltonian_is_hermitian"
    results = [r for r in run_evidence_checks(claim) if not r.skipped]
    assert any(r.evidence_id == "python_hermiticity" and r.ok for r in results)

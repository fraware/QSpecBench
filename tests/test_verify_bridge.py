"""Tests for verify-bridge CLI and semantic bridge validation."""

from __future__ import annotations

import tempfile
from fractions import Fraction
from pathlib import Path

import yaml

from qspecbench.denotate import denotate_ops, matrices_equal, matrix_from_qasm_json, ops_from_qasm_matrix
from qspecbench.qasm_matrix import _cnot, extract_matrix
from qspecbench.validate import validate_path
from qspecbench.verify_bridge import verify_bridge, write_bridge_result

REPO = Path(__file__).resolve().parents[1]

KERNEL_CHECKED = [
    "benchmarks/equivalence/cnot_self_inverse_cancellation",
    "benchmarks/equivalence/hadamard_conjugates_x_to_z",
    "benchmarks/equivalence/single_qubit_gate_cancellation",
    "benchmarks/equivalence/qft_inverse_qft_small_instance",
    "benchmarks/equivalence/clifford_simplification_preserves_unitary",
    "benchmarks/equivalence/source_optimized_qasm_equivalence_small_instance",
    "benchmarks/equivalence/phase_polynomial_equivalence_small_instance",
    "benchmarks/algorithms/teleportation_preserves_state_up_to_pauli_correction",
    "benchmarks/equivalence/rx_gate_equivalence_small_instance",
    "benchmarks/algorithms/bell_state_preparation",
]


def test_verify_bridge_kernel_checked_benchmarks():
    for rel in KERNEL_CHECKED:
        claim = REPO / rel
        result = write_bridge_result(claim)
        assert result["ok"], f"bridge verify failed for {rel}: {result.get('errors')}"


def test_verify_bridge_reads_semantic_bridge():
    claim = REPO / KERNEL_CHECKED[0]
    result = verify_bridge(claim)
    assert result["claimed_link"] == "kernel_checked"
    assert "lean_module" in result


def test_kernel_checked_validates_with_bridge_evidence():
    claim = REPO / KERNEL_CHECKED[0]
    spec_path = claim / "spec.yaml"
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    assert any(e.get("id") == "bridge_verify" for e in spec.get("evidence", []))
    results = validate_path(claim)
    assert results and results[0].ok


def test_cnot_control_target_directions_differ():
    cx01 = _cnot(2, 0, 1)
    cx10 = _cnot(2, 1, 0)
    assert cx01 != cx10
    assert cx01[1][3] == Fraction(1)
    assert cx10[2][3] == Fraction(1)


def test_denotate_cx_10_matches_qasm_matrix():
    qasm = "OPENQASM 3.0;\ninclude \"stdgates.inc\";\nqubit[2] q;\ncx q[1], q[0];\n"
    with tempfile.NamedTemporaryFile("w", suffix=".qasm", delete=False, encoding="utf-8") as f:
        f.write(qasm)
        path = Path(f.name)
    try:
        data = extract_matrix(path)
        ops = ops_from_qasm_matrix(data)
        denoted = denotate_ops(data["n_qubits"], ops)
        qasm_mat = matrix_from_qasm_json(data)
        assert matrices_equal(qasm_mat, denoted)
        assert denoted == _cnot(2, 1, 0)
    finally:
        path.unlink(missing_ok=True)

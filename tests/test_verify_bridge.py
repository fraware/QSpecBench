"""Tests for verify-bridge CLI and semantic bridge validation."""

from __future__ import annotations

import tempfile
from fractions import Fraction
from pathlib import Path

import yaml

from qspecbench.denotate import denotate_ops, matrix_from_qasm_json, ops_from_qasm_matrix
from qspecbench.qasm_matrix import _cnot, extract_matrix, matrices_equal
from qspecbench.validate import validate_path
from qspecbench.verify_bridge import verify_bridge, write_bridge_result

REPO = Path(__file__).resolve().parents[1]

PYTHON_CONSISTENCY_CHECKED = [
    "benchmarks/equivalence/hadamard_conjugates_x_to_z",
    "benchmarks/equivalence/single_qubit_gate_cancellation",
    "benchmarks/equivalence/qft_inverse_qft_small_instance",
    "benchmarks/equivalence/clifford_simplification_preserves_unitary",
    "benchmarks/equivalence/source_optimized_qasm_equivalence_small_instance",
    "benchmarks/equivalence/phase_polynomial_equivalence_small_instance",
    "benchmarks/algorithms/teleportation_preserves_state_up_to_pauli_correction",
    "benchmarks/equivalence/rx_gate_equivalence_small_instance",
    "benchmarks/algorithms/bell_state_preparation",
    "benchmarks/algorithms/swap_from_three_cx",
    "benchmarks/equivalence/toffoli_decomposition_equivalence",
    "benchmarks/equivalence/circuit_identity_after_layout",
    "benchmarks/algorithms/qft_then_inverse_qft_identity_up_to_ordering",
]


KERNEL_CHECKED = [
    "benchmarks/equivalence/cnot_self_inverse_cancellation",
    "benchmarks/equivalence/hadamard_conjugates_x_to_z",
    "benchmarks/equivalence/single_qubit_gate_cancellation",
    "benchmarks/equivalence/qft_inverse_qft_small_instance",
    "benchmarks/algorithms/swap_from_three_cx",
    "benchmarks/equivalence/toffoli_decomposition_equivalence",
    "benchmarks/equivalence/circuit_identity_after_layout",
    "benchmarks/equivalence/source_optimized_qasm_equivalence_small_instance",
    "benchmarks/algorithms/bell_state_preparation",
    "benchmarks/equivalence/clifford_simplification_preserves_unitary",
    "benchmarks/equivalence/phase_polynomial_equivalence_small_instance",
]


def test_verify_bridge_python_consistency_checked_benchmarks():
    for rel in PYTHON_CONSISTENCY_CHECKED:
        claim = REPO / rel
        result = write_bridge_result(claim)
        assert result["ok"], f"bridge verify failed for {rel}: {result.get('errors')}"


def test_verify_bridge_kernel_checked_cnot():
    claim = REPO / KERNEL_CHECKED[0]
    result = verify_bridge(claim)
    assert result["claimed_link"] == "kernel_checked"
    assert result["ok"]


def test_verify_bridge_all_kernel_checked_benchmarks():
    for rel in KERNEL_CHECKED:
        claim = REPO / rel
        result = verify_bridge(claim)
        assert result["claimed_link"] == "kernel_checked", rel
        assert result["ok"], f"{rel}: {result.get('errors')}"


def test_kernel_bridge_accepts_clifford_with_manifest():
    """Clifford S gate uses complex denotation; manifest includes bridge_clifford_hhs."""
    import json
    import yaml
    from qspecbench.bridge_manifest import validate_kernel_bridge

    claim = REPO / "benchmarks/equivalence/clifford_simplification_preserves_unitary"
    spec = yaml.safe_load((claim / "spec.yaml").read_text(encoding="utf-8"))
    bridge = json.loads((claim / "expected/semantic_bridge.json").read_text(encoding="utf-8"))
    errors = validate_kernel_bridge(claim, bridge, spec)
    assert not errors, errors


def test_kernel_bridge_accepts_phase_polynomial_with_manifest():
    import json
    import yaml
    from qspecbench.bridge_manifest import validate_kernel_bridge

    claim = REPO / "benchmarks/equivalence/phase_polynomial_equivalence_small_instance"
    spec = yaml.safe_load((claim / "spec.yaml").read_text(encoding="utf-8"))
    bridge = json.loads((claim / "expected/semantic_bridge.json").read_text(encoding="utf-8"))
    errors = validate_kernel_bridge(claim, bridge, spec)
    assert not errors, errors


def test_st_denotation_matches_qasm_matrix():
    """Python extract_matrix and denotate_ops agree on circuits with S/T phase gates."""
    from qspecbench.qasm_matrix import extract_matrix, matrices_equal

    circuits = [
        "OPENQASM 3.0;\nqubit[1] q;\ns q[0];\n",
        "OPENQASM 3.0;\nqubit[1] q;\nt q[0];\n",
        "OPENQASM 3.0;\nqubit[1] q;\nsdg q[0];\n",
        "OPENQASM 3.0;\nqubit[1] q;\ntdg q[0];\n",
        "OPENQASM 3.0;\nqubit[1] q;\nh q[0];\ns q[0];\n",
        "OPENQASM 3.0;\nqubit[1] q;\nh q[0];\nh q[0];\ns q[0];\n",
    ]
    for qasm in circuits:
        with tempfile.NamedTemporaryFile("w", suffix=".qasm", delete=False, encoding="utf-8") as f:
            f.write(qasm)
            path = Path(f.name)
        try:
            data = extract_matrix(path)
            ops = ops_from_qasm_matrix(data)
            denoted = denotate_ops(data["n_qubits"], ops)
            qasm_mat = matrix_from_qasm_json(data)
            assert matrices_equal(qasm_mat, denoted), qasm
        finally:
            path.unlink(missing_ok=True)


def test_kernel_bridge_rejects_missing_manifest_theorem():
    from qspecbench.bridge_manifest import validate_kernel_bridge
    import json
    import yaml

    claim = REPO / "benchmarks/equivalence/rx_gate_equivalence_small_instance"
    spec = yaml.safe_load((claim / "spec.yaml").read_text(encoding="utf-8"))
    bridge = json.loads((claim / "expected/semantic_bridge.json").read_text(encoding="utf-8"))
    bridge = dict(bridge)
    bridge["claimed_link"] = "kernel_checked"
    errors = validate_kernel_bridge(claim, bridge, spec)
    assert errors


def test_verify_bridge_reads_semantic_bridge():
    claim = REPO / KERNEL_CHECKED[0]
    result = verify_bridge(claim)
    assert result["claimed_link"] == "kernel_checked"
    assert "lean_module" in result


def test_python_consistency_checked_validates_with_bridge_evidence():
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
    assert cx01[1][3] == (Fraction(1), Fraction(0))
    assert cx10[2][3] == (Fraction(1), Fraction(0))


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

"""Tests for verify-bridge CLI and semantic bridge validation."""

from __future__ import annotations

import json
import tempfile
from fractions import Fraction
from pathlib import Path

import yaml

from qspecbench.bridge_manifest import validate_lean_evidence_anchor, validate_manifest_bridge
from qspecbench.denotate import denotate_ops, matrix_from_qasm_json, ops_from_qasm_matrix
from qspecbench.qasm_matrix import _cnot, _parse_angle, extract_matrix, matrices_equal
from qspecbench.validate import validate_path
from qspecbench.verify_bridge import verify_bridge, write_bridge_result

REPO = Path(__file__).resolve().parents[1]

PYTHON_DENOTATION_CONSISTENCY = [
    "benchmarks/algorithms/teleportation_preserves_state_up_to_pauli_correction",
    "benchmarks/algorithms/qft_then_inverse_qft_identity_up_to_ordering",
]

KERNEL_CHECKED = [
    "benchmarks/equivalence/cnot_self_inverse_cancellation",
    "benchmarks/equivalence/hadamard_conjugates_x_to_z",
    "benchmarks/equivalence/single_qubit_gate_cancellation",
    "benchmarks/algorithms/bell_state_preparation",
    "benchmarks/algorithms/swap_from_three_cx",
    "benchmarks/equivalence/toffoli_decomposition_equivalence",
]

MANIFEST_CHECKED = [
    "benchmarks/equivalence/rx_gate_equivalence_small_instance",
    "benchmarks/equivalence/qft_inverse_qft_small_instance",
    "benchmarks/equivalence/circuit_identity_after_layout",
    "benchmarks/equivalence/source_optimized_qasm_equivalence_small_instance",
    "benchmarks/equivalence/clifford_simplification_preserves_unitary",
    "benchmarks/equivalence/phase_polynomial_equivalence_small_instance",
]


def test_verify_bridge_python_denotation_benchmarks():
    for rel in PYTHON_DENOTATION_CONSISTENCY:
        claim = REPO / rel
        result = write_bridge_result(claim)
        assert result["ok"], f"bridge verify failed for {rel}: {result.get('errors')}"
        assert result["claimed_link"] == "python_denotation_consistency", rel


def test_verify_bridge_kernel_checked_cnot():
    claim = REPO / KERNEL_CHECKED[0]
    result = verify_bridge(claim)
    assert result["claimed_link"] == "kernel_checked_codegen_trace"
    assert result["ok"]


def test_verify_bridge_all_kernel_checked_benchmarks():
    for rel in KERNEL_CHECKED:
        claim = REPO / rel
        result = verify_bridge(claim)
        assert result["claimed_link"] == "kernel_checked_codegen_trace", rel
        assert result["ok"], f"{rel}: {result.get('errors')}"


def test_verify_bridge_manifest_checked_cnot():
    claim = REPO / KERNEL_CHECKED[0]
    result = verify_bridge(claim)
    assert result["claimed_link"] == "kernel_checked_codegen_trace"
    assert result["ok"]


def test_verify_bridge_all_manifest_checked_benchmarks():
    for rel in MANIFEST_CHECKED:
        claim = REPO / rel
        result = verify_bridge(claim)
        assert result["claimed_link"] == "manifest_checked_theorem_binding", rel
        assert result["ok"], f"{rel}: {result.get('errors')}"


def test_manifest_bridge_accepts_clifford_with_manifest():
    claim = REPO / "benchmarks/equivalence/clifford_simplification_preserves_unitary"
    spec = yaml.safe_load((claim / "spec.yaml").read_text(encoding="utf-8"))
    bridge = json.loads((claim / "expected" / "semantic_bridge.json").read_text(encoding="utf-8"))
    errors = validate_manifest_bridge(claim, bridge, spec)
    assert not errors, errors


def test_manifest_bridge_accepts_phase_polynomial_with_manifest():
    claim = REPO / "benchmarks/equivalence/phase_polynomial_equivalence_small_instance"
    spec = yaml.safe_load((claim / "spec.yaml").read_text(encoding="utf-8"))
    bridge = json.loads((claim / "expected" / "semantic_bridge.json").read_text(encoding="utf-8"))
    errors = validate_manifest_bridge(claim, bridge, spec)
    assert not errors, errors


def test_st_denotation_matches_qasm_matrix():
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


def test_manifest_bridge_rejects_missing_manifest_theorem():
    claim = REPO / "benchmarks/algorithms/qft_then_inverse_qft_identity_up_to_ordering"
    spec = yaml.safe_load((claim / "spec.yaml").read_text(encoding="utf-8"))
    bridge_path = claim / "expected" / "semantic_bridge.json"
    if not bridge_path.is_file():
        return
    bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
    bridge = dict(bridge)
    bridge["claimed_link"] = "manifest_checked_theorem_binding"
    bridge["lean_theorem"] = "nonexistent_theorem_xyz"
    errors = validate_manifest_bridge(claim, bridge, spec)
    assert errors


def test_verify_bridge_reads_semantic_bridge():
    claim = REPO / KERNEL_CHECKED[0]
    result = verify_bridge(claim)
    assert result["claimed_link"] == "kernel_checked_codegen_trace"
    assert "lean_module" in result


def test_manifest_checked_validates_with_bridge_evidence():
    claim = REPO / KERNEL_CHECKED[0]
    spec = yaml.safe_load((claim / "spec.yaml").read_text(encoding="utf-8"))
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


def test_unified_angle_parsing_cp_pi_over_2():
    qasm = "OPENQASM 3.0;\nqubit[2] q;\ncp(pi/2) q[0], q[1];\n"
    with tempfile.NamedTemporaryFile("w", suffix=".qasm", delete=False, encoding="utf-8") as f:
        f.write(qasm)
        path = Path(f.name)
    try:
        assert _parse_angle("pi/2") == _parse_angle("1.5707963267948966")
        data = extract_matrix(path)
        ops = ops_from_qasm_matrix(data)
        denoted = denotate_ops(data["n_qubits"], ops)
        qasm_mat = matrix_from_qasm_json(data)
        assert matrices_equal(qasm_mat, denoted)
    finally:
        path.unlink(missing_ok=True)


def test_lean_anchor_rejects_comment_only_theorem():
    text = """
import QSpecBench.Quantum.OpenQASM3
/- mentions QSpecBench.Quantum.OpenQASM3.bridge_cnot_self_inverse in prose -/
"""
    errors = validate_lean_evidence_anchor(
        text,
        benchmark_id="cnot_self_inverse_cancellation",
        theorem="QSpecBench.Quantum.OpenQASM3.bridge_cnot_self_inverse",
        artifact_sha256="a" * 64,
        gate_trace_sha256="b" * 64,
    )
    assert errors


def test_lean_anchor_rejects_wrong_hash():
    anchor = """/- QSpecBench evidence:
benchmark_id = "cnot_self_inverse_cancellation"
obligation_id = "semantic_bridge"
theorem = "QSpecBench.Quantum.OpenQASM3.bridge_cnot_self_inverse"
artifact_sha256 = "0000000000000000000000000000000000000000000000000000000000000000"
gate_trace_sha256 = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
-/
#check QSpecBench.Quantum.OpenQASM3.bridge_cnot_self_inverse
"""
    errors = validate_lean_evidence_anchor(
        anchor,
        benchmark_id="cnot_self_inverse_cancellation",
        theorem="QSpecBench.Quantum.OpenQASM3.bridge_cnot_self_inverse",
        artifact_sha256="a" * 64,
        gate_trace_sha256="b" * 64,
    )
    assert any("artifact_sha256" in e for e in errors)

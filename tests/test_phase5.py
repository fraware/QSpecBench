"""Phase 5 infrastructure tests."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import yaml

from qspecbench.bridge_codegen import build_canonical_ast
from qspecbench.dynamic_simulation_evidence import (
    attach_fingerprint,
    regenerate_dynamic_simulation_report,
    validate_dynamic_simulation_evidence,
)
from qspecbench.dynamic_simulator import (
    _MEASURE_LINE,
    state_after_unitary_prefix,
    state_after_unitary_prefix_normalized,
    verify_teleportation_basis_states,
)
from qspecbench.qec_external import validate_qec_external_certificate
from qspecbench.qasm_matrix import UnsupportedQasmError, extract_matrix

REPO = Path(__file__).resolve().parents[1]
TELEPORT = REPO / "benchmarks" / "algorithms" / "teleportation_preserves_state_up_to_pauli_correction"
DIST_CERT = REPO / "benchmarks" / "qec" / "distance_certificate_small_css_code"


def test_teleportation_basis_operational_check():
    spec = yaml.safe_load((TELEPORT / "spec.yaml").read_text(encoding="utf-8"))
    report = verify_teleportation_basis_states(
        TELEPORT / "artifacts" / "teleportation.qasm",
        spec.get("qasm_extraction"),
    )
    assert report["type"] == "teleportation_basis_check_v0"
    assert report["gate_model"] == "complex_normalized_unitary_prefix"
    assert len(report["results"]) == 2
    out = TELEPORT / "evidence" / "dynamic_simulation_basis_check.json"
    out.write_text(json.dumps(attach_fingerprint(report), indent=2) + "\n", encoding="utf-8")
    assert out.is_file()
    assert report["all_ok"] is True
    assert report.get("failure_mode") is None
    assert report["int_scaffold_diagnostic"]["all_ok"] is False
    assert "calibration_note" in report


def test_dynamic_simulation_evidence_freshness_passes():
    spec = yaml.safe_load((TELEPORT / "spec.yaml").read_text(encoding="utf-8"))
    report = regenerate_dynamic_simulation_report(TELEPORT, spec)
    assert report is not None
    path = TELEPORT / "evidence" / "dynamic_simulation_basis_check.json"
    path.write_text(json.dumps(attach_fingerprint(report), indent=2) + "\n", encoding="utf-8")
    errors = validate_dynamic_simulation_evidence(TELEPORT, spec)
    assert errors == [], errors


def test_dynamic_simulation_evidence_stale_fails():
    spec = yaml.safe_load((TELEPORT / "spec.yaml").read_text(encoding="utf-8"))
    path = TELEPORT / "evidence" / "dynamic_simulation_basis_check.json"
    stale = {"type": "teleportation_basis_check_v0", "all_ok": False, "results": []}
    path.write_text(json.dumps(stale, indent=2) + "\n", encoding="utf-8")
    errors = validate_dynamic_simulation_evidence(TELEPORT, spec)
    assert errors
    report = regenerate_dynamic_simulation_report(TELEPORT, spec)
    path.write_text(json.dumps(attach_fingerprint(report), indent=2) + "\n", encoding="utf-8")


def test_normalized_prefix_differs_from_int_scaffold():
    spec = yaml.safe_load((TELEPORT / "spec.yaml").read_text(encoding="utf-8"))
    qasm = TELEPORT / "artifacts" / "teleportation.qasm"
    extraction = spec.get("qasm_extraction")
    init = {0: (Fraction(1), Fraction(0))}
    _, st_norm = state_after_unitary_prefix_normalized(qasm, extraction, init)
    _, st_int = state_after_unitary_prefix(qasm, extraction, init)
    assert st_norm != st_int


def test_state_after_unitary_prefix_nontrivial():
    spec = yaml.safe_load((TELEPORT / "spec.yaml").read_text(encoding="utf-8"))
    n, st = state_after_unitary_prefix(
        TELEPORT / "artifacts" / "teleportation.qasm",
        spec.get("qasm_extraction"),
        {0: (Fraction(1), Fraction(0))},
    )
    assert n == 3
    assert sum(float(r * r + i * i) for r, i in st) > 0.99


def test_dynamic_simulator_measurements_recorded():
    assert _MEASURE_LINE.match("c[0] = measure q[0];")
    spec = yaml.safe_load((TELEPORT / "spec.yaml").read_text(encoding="utf-8"))
    report = verify_teleportation_basis_states(
        TELEPORT / "artifacts" / "teleportation.qasm",
        spec.get("qasm_extraction"),
    )
    assert report["results"], report


def test_unitary_fragment_fail_closed_on_measure():
    yaml.safe_load((TELEPORT / "spec.yaml").read_text(encoding="utf-8"))
    try:
        extract_matrix(
            TELEPORT / "artifacts" / "teleportation.qasm",
            extraction={"mode": "unitary_fragment", "allowed_to_skip": []},
        )
        raise AssertionError("expected UnsupportedQasmError")
    except UnsupportedQasmError:
        pass


def test_qec_external_witness_bruteforce_requires_scope():
    cert = {
        "certificate_version": "0.2-external",
        "claim_kind": "minimum_distance",
        "code_ref": {"artifact_sha256": "a" * 64},
        "prover": {"name": "test", "method": "external_prover"},
        "result": {
            "status": "unknown",
            "computed_value": 4,
            "witness": {"min_distance": 4, "method": "bruteforce_weight_enumeration"},
        },
    }
    errors = validate_qec_external_certificate(cert, DIST_CERT, {"id": "distance_certificate_small_css_code"})
    assert any("complete_for" in e for e in errors)


def test_qec_external_proved_requires_witness_hash():
    cert = {
        "certificate_version": "0.2-external",
        "claim_kind": "minimum_distance",
        "code_ref": {"artifact_sha256": "b" * 64},
        "prover": {"name": "test", "method": "external_prover"},
        "result": {
            "status": "proved",
            "computed_value": 3,
            "witness": {"min_distance": 3},
        },
    }
    errors = validate_qec_external_certificate(cert, DIST_CERT, {"id": "x"})
    assert any("proof_artifact_sha256" in e for e in errors)


def _lean_mirror_parse_line_qasm_op(line: str) -> dict[str, object] | None:
    """Mirror Lean ``OpenQASM3Parser.parseLineQasmOp`` (H/X/CX only)."""
    pg = _lean_mirror_parse_gate_line(line)
    if pg is None:
        return None
    if pg["op"] == "rx":
        return None
    return pg


def _lean_mirror_parse_lines(lines: list[str]) -> list[dict[str, object]]:
    parsed: list[dict[str, object]] = []
    for raw in lines:
        entry = _lean_mirror_parse_line_qasm_op(raw)
        if entry is not None:
            parsed.append(entry)
    return parsed


def test_lean_parser_parse_lines_match_codegen_traces():
    for qasm in KERNEL_CHECKED_QASM:
        ast = build_canonical_ast(qasm)
        lines = qasm.read_text(encoding="utf-8").splitlines()
        parsed = _lean_mirror_parse_lines(lines)
        assert [g["op"] for g in ast["gates"]] == [p["op"] for p in parsed], qasm
        assert [g["qubits"] for g in ast["gates"]] == [p["qubits"] for p in parsed], qasm


def test_lean_parser_stub_file_exists():
    path = REPO / "lean" / "QSpecBench" / "Quantum" / "OpenQASM3Parser.lean"
    text = path.read_text(encoding="utf-8")
    assert "parseGateLine" in text
    assert "parseLines" in text
    assert "parseLines_bell_eq_generated_ops" in text or "parseLines_bell_eq_bell_prep_ops" in text
    assert "parserTrustBoundaryNote" in text
    assert 'parseGateLine "cx q[0], q[1];"' in text


def _lean_mirror_parse_gate_line(line: str) -> dict[str, object] | None:
    """Mirror Lean ``OpenQASM3Parser.parseGateLine`` for cross-check tests."""
    s = line.strip().rstrip(";").strip()
    if not s or s.startswith("//") or s.lower().startswith("openqasm"):
        return None
    if s.lower().startswith("include"):
        return None

    def _qubit(tok: str) -> int | None:
        t = tok.strip()
        if t.startswith("q[") and t.endswith("]"):
            return int(t[2:-1])
        if t.startswith("q") and t[1:].isdigit():
            return int(t[1:])
        return None

    if s.startswith("h "):
        q = _qubit(s[2:])
        return {"op": "h", "qubits": [q]} if q is not None else None
    if s.startswith("x "):
        q = _qubit(s[2:])
        return {"op": "x", "qubits": [q]} if q is not None else None
    if s.startswith("cx ") or s.startswith("cnot "):
        rest = s.split(" ", 1)[1]
        parts = [p.strip() for p in rest.split(",")]
        if len(parts) != 2:
            return None
        c, t = _qubit(parts[0]), _qubit(parts[1])
        if c is None or t is None:
            return None
        return {"op": "cx", "qubits": [c, t]}
    return None


KERNEL_CHECKED_QASM = [
    REPO / "benchmarks" / "algorithms" / "bell_state_preparation" / "artifacts" / "circuit.qasm",
    REPO / "benchmarks" / "equivalence" / "cnot_self_inverse_cancellation" / "artifacts" / "source.qasm",
    REPO / "benchmarks" / "equivalence" / "hadamard_conjugates_x_to_z" / "artifacts" / "source.qasm",
    REPO / "benchmarks" / "equivalence" / "single_qubit_gate_cancellation" / "artifacts" / "source.qasm",
    REPO / "benchmarks" / "algorithms" / "swap_from_three_cx" / "artifacts" / "source.qasm",
]


def test_lean_parser_gate_lines_match_canonical_ast():
    for qasm in KERNEL_CHECKED_QASM:
        ast = build_canonical_ast(qasm)
        parsed: list[dict[str, object]] = []
        for raw in qasm.read_text(encoding="utf-8").splitlines():
            entry = _lean_mirror_parse_gate_line(raw)
            if entry is not None:
                parsed.append(entry)
        assert [g["op"] for g in ast["gates"]] == [p["op"] for p in parsed], qasm
        assert [g["qubits"] for g in ast["gates"]] == [p["qubits"] for p in parsed], qasm


def test_int_scaffold_vs_operational_h_on_q0_three_qubits():
    """H on q[0] differs between verify-bridge Kronecker order and operational wire model."""
    from qspecbench.dynamic_simulator import _tensor_product_on_qubit
    from qspecbench.qasm_matrix import _apply_single, _single_qubit_gate

    n = 3
    q = 0
    op_int = _apply_single(n, "h", q)
    op_oper = _tensor_product_on_qubit(n, q, _single_qubit_gate("h"))
    assert op_int != op_oper


def test_measurement_lean_scaffold_exists():
    path = REPO / "lean" / "QSpecBench" / "Quantum" / "Measurement.lean"
    text = path.read_text(encoding="utf-8")
    assert "measure_state00_q0_zero" in text
    assert "joint_state00_zz" in text
    assert "syndrome00_from_state00" in text
    assert "measurementTrustBoundaryNote" in text


def test_teleportation_feedforward_artifact_basis_check():
    spec = yaml.safe_load((TELEPORT / "spec.yaml").read_text(encoding="utf-8"))
    ff = TELEPORT / "artifacts" / "teleportation_with_feedforward.qasm"
    assert ff.is_file()
    report = verify_teleportation_basis_states(
        ff, spec.get("qasm_extraction"), artifact_role="supplementary_feedforward",
    )
    assert report["artifact_role"] == "supplementary_feedforward"
    assert report["all_ok"] is True

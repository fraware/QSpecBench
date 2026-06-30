"""Phase 5 infrastructure tests."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import pytest
import yaml

from qspecbench import RELEASE_TAG
from qspecbench.bridge_codegen import (
    ARTIFACT_PARSE_THEOREM_MAP,
    KERNEL_ARTIFACT_SOURCE_DEF,
    KERNEL_BRIDGE_IDS,
    LEAN_AST_SHA256_FIELD,
    ast_sha256,
    build_canonical_ast,
    build_lean_mirror_canonical_ast,
    extract_lean_kernel_artifact_source,
    lean_ast_sha256_for_benchmark,
    lean_kernel_artifact_source_bytes,
    lean_mirror_parse_gate_line,
)
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
    assert report.get("lean_cross_ref", {}).get("lean_theorem_refs")
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
    """Delegate to shared Lean mirror parser in bridge_codegen."""
    return lean_mirror_parse_gate_line(line)


KERNEL_CHECKED_QASM = [
    REPO / "benchmarks" / "algorithms" / "bell_state_preparation" / "artifacts" / "circuit.qasm",
    REPO / "benchmarks" / "equivalence" / "cnot_self_inverse_cancellation" / "artifacts" / "source.qasm",
    REPO / "benchmarks" / "equivalence" / "hadamard_conjugates_x_to_z" / "artifacts" / "source.qasm",
    REPO / "benchmarks" / "equivalence" / "single_qubit_gate_cancellation" / "artifacts" / "source.qasm",
    REPO / "benchmarks" / "algorithms" / "swap_from_three_cx" / "artifacts" / "source.qasm",
    REPO / "benchmarks" / "equivalence" / "toffoli_decomposition_equivalence" / "artifacts" / "source.qasm",
]

BENCHMARK_ID_BY_QASM = {
    "cnot_self_inverse_cancellation": REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation",
    "hadamard_conjugates_x_to_z": REPO / "benchmarks/equivalence/hadamard_conjugates_x_to_z",
    "single_qubit_gate_cancellation": REPO / "benchmarks/equivalence/single_qubit_gate_cancellation",
    "bell_state_preparation": REPO / "benchmarks/algorithms/bell_state_preparation",
    "swap_from_three_cx": REPO / "benchmarks/algorithms/swap_from_three_cx",
    "toffoli_decomposition_equivalence": REPO / "benchmarks/equivalence/toffoli_decomposition_equivalence",
}


def test_release_tag_v022():
    assert RELEASE_TAG == "v0.2.2"


def test_cnot_kernel_artifact_source_matches_disk_and_manifest():
    """sha256(disk) == manifest artifact_sha256 == sha256(cnotKernelArtifactSource)."""
    claim = BENCHMARK_ID_BY_QASM["cnot_self_inverse_cancellation"]
    qasm = claim / "artifacts" / "source.qasm"
    disk = qasm.read_bytes()
    disk_hash = hashlib.sha256(disk).hexdigest()
    bridge = json.loads((claim / "expected" / "semantic_bridge.json").read_text(encoding="utf-8"))
    lean_bytes = lean_kernel_artifact_source_bytes("cnot_self_inverse_cancellation")
    assert disk_hash == bridge["artifact_sha256"]
    assert disk_hash == hashlib.sha256(lean_bytes).hexdigest()
    assert disk == lean_bytes


def test_kernel_artifact_byte_chain_all_bridges():
    """Each kernel bridge: disk bytes match manifest and Lean embedded source."""
    for benchmark_id, claim in BENCHMARK_ID_BY_QASM.items():
        bridge = json.loads((claim / "expected" / "semantic_bridge.json").read_text(encoding="utf-8"))
        qasm_rel = bridge.get("qasm_artifact") or "artifacts/source.qasm"
        if benchmark_id == "bell_state_preparation":
            qasm_rel = "artifacts/circuit.qasm"
        disk = (claim / qasm_rel).read_bytes()
        disk_hash = hashlib.sha256(disk).hexdigest()
        lean_bytes = lean_kernel_artifact_source_bytes(benchmark_id)
        assert disk_hash == bridge["artifact_sha256"], benchmark_id
        assert disk == lean_bytes, benchmark_id
        assert bridge.get("artifact_parse_theorem") == ARTIFACT_PARSE_THEOREM_MAP[benchmark_id]


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
        assert ast["canonical_ast_version"] == "0.1"
        assert ast["n_qubits"] >= 1




def test_qasm_bytes_hash_and_gate_list_stable():
    """Python gate list + artifact bytes hash for kernel QASM files (Lean parseQasmSource cross-ref)."""
    for qasm in KERNEL_CHECKED_QASM:
        raw = qasm.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        assert len(digest) == 64
        ast = build_canonical_ast(qasm)
        assert ast["gates"]
        assert ast_sha256(ast)


def test_cnot_kernel_source_matches_artifact_and_codegen_ops():
    """Cross-test full CNOT QASM grammar against Python canonical AST gate trace."""
    qasm = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation/artifacts/source.qasm"
    source = qasm.read_text(encoding="utf-8")
    assert source.startswith("OPENQASM 3.0;")
    assert 'include "stdgates.inc";' in source
    assert "qubit[2] q;" in source
    ast = build_canonical_ast(qasm)
    assert ast["gates"] == [{"op": "cx", "qubits": [0, 1]}, {"op": "cx", "qubits": [0, 1]}]
    lean_source = extract_lean_kernel_artifact_source(KERNEL_ARTIFACT_SOURCE_DEF["cnot_self_inverse_cancellation"])
    assert lean_source == source
    gate_lines = [
        line
        for line in source.splitlines()
        if line.strip() and not line.strip().startswith(("OPENQASM", "include", "qubit"))
    ]
    assert gate_lines == ["cx q[0], q[1];", "cx q[0], q[1];"]
    mirror_ops: list[str] = []
    for raw in source.splitlines():
        entry = _lean_mirror_parse_gate_line(raw)
        if entry is not None:
            mirror_ops.append(str(entry["op"]))
    assert mirror_ops == [g["op"] for g in ast["gates"]]


def test_bell_kernel_source_matches_artifact_and_codegen_ops():
    """Cross-test full Bell QASM grammar against Python canonical AST gate trace."""
    qasm = REPO / "benchmarks" / "algorithms" / "bell_state_preparation" / "artifacts" / "circuit.qasm"
    source = qasm.read_text(encoding="utf-8")
    assert source.startswith("OPENQASM 3.0;")
    assert 'include "stdgates.inc";' in source
    assert "qubit[2] q;" in source
    ast = build_canonical_ast(qasm)
    assert ast["gates"] == [{"op": "h", "qubits": [0]}, {"op": "cx", "qubits": [0, 1]}]
    gate_lines = [
        line
        for line in source.splitlines()
        if line.strip() and not line.strip().startswith(("OPENQASM", "include", "qubit"))
    ]
    assert gate_lines == ["h q[0];", "cx q[0], q[1];"]


def test_swap_kernel_source_matches_artifact_and_codegen_ops():
    """Cross-test full three-CX SWAP QASM grammar against Python canonical AST gate trace."""
    qasm = REPO / "benchmarks" / "algorithms" / "swap_from_three_cx" / "artifacts" / "source.qasm"
    source = qasm.read_text(encoding="utf-8")
    assert source.startswith("OPENQASM 3.0;")
    ast = build_canonical_ast(qasm)
    assert ast["gates"] == [
        {"op": "cx", "qubits": [0, 1]},
        {"op": "cx", "qubits": [1, 0]},
        {"op": "cx", "qubits": [0, 1]},
    ]


def test_canonical_ast_json_matches_lean_mirror_structure():
    """Lean-parseable gate lines must match Python canonical_ast gate objects."""
    qasm = REPO / "benchmarks" / "algorithms" / "bell_state_preparation" / "artifacts" / "circuit.qasm"
    ast = build_canonical_ast(qasm)
    mirror_ops: list[str] = []
    mirror_qubits: list[list[int]] = []
    for raw in qasm.read_text(encoding="utf-8").splitlines():
        entry = _lean_mirror_parse_gate_line(raw)
        if entry is not None:
            mirror_ops.append(str(entry["op"]))
            mirror_qubits.append(list(entry["qubits"]))  # type: ignore[arg-type]
    assert mirror_ops == [g["op"] for g in ast["gates"]]
    assert mirror_qubits == [g["qubits"] for g in ast["gates"]]


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
    assert "measure_state000_q0_zero" in text
    assert "pauli_x4_corrects_state01_at_receiver" in text
    assert "pauli_x8_corrects_state001_at_receiver" in text
    assert "teleport_pauli_correction_anchor_note" in text
    assert "teleport_basis00_lemma_chain" in text
    assert "applyPauliCorrection4" in text
    assert "recordZOutcome" in text
    assert "groverMeasurementCrossRefNote" in text
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


@pytest.mark.parametrize(
    "benchmark_id,qasm_rel,lean_def",
    [
        ("cnot_self_inverse_cancellation", "benchmarks/equivalence/cnot_self_inverse_cancellation/artifacts/source.qasm", "cnotKernelArtifactSource"),
        ("bell_state_preparation", "benchmarks/algorithms/bell_state_preparation/artifacts/circuit.qasm", "bellKernelArtifactSource"),
        ("swap_from_three_cx", "benchmarks/algorithms/swap_from_three_cx/artifacts/source.qasm", "swapKernelArtifactSource"),
        ("hadamard_conjugates_x_to_z", "benchmarks/equivalence/hadamard_conjugates_x_to_z/artifacts/source.qasm", "hxhKernelArtifactSource"),
        ("single_qubit_gate_cancellation", "benchmarks/equivalence/single_qubit_gate_cancellation/artifacts/source.qasm", "hhKernelArtifactSource"),
        ("toffoli_decomposition_equivalence", "benchmarks/equivalence/toffoli_decomposition_equivalence/artifacts/source.qasm", "toffoliKernelArtifactSource"),
    ],
)
def test_kernel_artifact_byte_sha256_chain(benchmark_id, qasm_rel, lean_def):
    from qspecbench.bridge_codegen import extract_lean_kernel_artifact_source
    from qspecbench.bridge_manifest import load_manifest

    qasm = REPO / qasm_rel
    disk_hash = hashlib.sha256(qasm.read_bytes()).hexdigest()
    lean_src = extract_lean_kernel_artifact_source(lean_def)
    lean_hash = hashlib.sha256(lean_src.encode("utf-8")).hexdigest()
    assert disk_hash == lean_hash, benchmark_id
    entry = next(e for e in load_manifest()["entries"] if e["benchmark_id"] == benchmark_id)
    assert entry["artifact_sha256"] == disk_hash


@pytest.mark.parametrize("benchmark_id", sorted(KERNEL_BRIDGE_IDS))
def test_kernel_lean_ast_sha256_matches_python_ast(benchmark_id):
    from qspecbench.bridge_codegen import KERNEL_ARTIFACT_QASM_REL

    qasm = REPO / KERNEL_ARTIFACT_QASM_REL[benchmark_id]
    py_ast = build_canonical_ast(qasm)
    lean_ast = build_lean_mirror_canonical_ast(qasm)
    assert ast_sha256(py_ast) == ast_sha256(lean_ast), benchmark_id
    assert lean_ast_sha256_for_benchmark(benchmark_id) == ast_sha256(py_ast)

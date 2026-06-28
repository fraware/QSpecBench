"""Additional tests for Phase 3 infrastructure."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import yaml

from qspecbench.bridge_codegen import theorem_identifier_sha256, verify_kernel_checked_entry
from qspecbench.bridge_manifest import load_manifest, validate_kernel_checked_bridge
from qspecbench.qasm_matrix import extract_matrix
from qspecbench.validate import validate_path

REPO = Path(__file__).resolve().parents[1]
MINIMAL = REPO / "schema" / "examples" / "minimal.spec.yaml"
CNOT_DIR = REPO / "benchmarks" / "equivalence" / "cnot_self_inverse_cancellation"
BELL_DIR = REPO / "benchmarks" / "algorithms" / "bell_state_preparation"
SWAP_DIR = REPO / "benchmarks" / "algorithms" / "swap_from_three_cx"
TELEPORT_DIR = REPO / "benchmarks" / "algorithms" / "teleportation_preserves_state_up_to_pauli_correction"


def _minimal_spec_text(**overrides: object) -> str:
    spec = yaml.safe_load(MINIMAL.read_text(encoding="utf-8"))
    spec.update(overrides)
    return yaml.dump(spec, sort_keys=False)


def test_full_dynamic_semantics_allowed_with_dynamic_circuit_base():
    results = validate_path(TELEPORT_DIR)
    assert results and results[0].ok, results[0].errors if results else "no results"


def test_full_dynamic_semantics_rejected_without_dynamic_circuit_base():
    with tempfile.TemporaryDirectory() as tmp:
        claim = Path(tmp)
        (claim / "spec.yaml").write_text(
            _minimal_spec_text(
                id="dynamic_mode_test",
                track="algorithm",
                domain="test",
                claim_type="test_claim",
                qasm_extraction={
                    "mode": "full_dynamic_semantics",
                    "allowed_to_skip": ["measurement"],
                },
                semantics_base="openqasm_fragment",
                claim_scope={
                    "headline_claim_id": "dynamic_mode_test_headline",
                    "headline_claim_text": "Dynamic mode fail-closed test",
                    "required_obligations": ["test"],
                },
                proved_scope={"checked_obligations": [], "unproved_obligations": ["test"]},
                headline_claim_status={"status": "unproved", "notes": None},
            ),
            encoding="utf-8",
        )
        results = validate_path(claim)
        assert results and not results[0].ok
        assert any("dynamic_circuit" in e for e in results[0].errors)


def test_teleportation_full_dynamic_extracts_unitary_prefix():
    spec = yaml.safe_load((TELEPORT_DIR / "spec.yaml").read_text(encoding="utf-8"))
    data = extract_matrix(
        TELEPORT_DIR / "artifacts" / "teleportation.qasm",
        extraction=spec.get("qasm_extraction"),
    )
    assert data.get("extraction_mode") == "dynamic_fragment_recording"
    assert data.get("measurement_semantics") == "projective_povm_stub"
    assert len(data.get("dynamic_fragments") or []) >= 2


def test_hadamard_kernel_checked_manifest_chain():
    entry = next(
        e for e in load_manifest()["entries"] if e["benchmark_id"] == "hadamard_conjugates_x_to_z"
    )
    assert entry.get("theorem_identifier_sha256") == theorem_identifier_sha256(
        "QSpecBench.Quantum.OpenQASM3.bridge_hadamard_codegen_conjugates_x"
    )
    had_dir = REPO / "benchmarks" / "equivalence" / "hadamard_conjugates_x_to_z"
    assert verify_kernel_checked_entry(entry, had_dir) == []


def test_single_qubit_gate_cancellation_kernel_checked_manifest_chain():
    entry = next(
        e for e in load_manifest()["entries"]
        if e["benchmark_id"] == "single_qubit_gate_cancellation"
    )
    assert entry.get("theorem_identifier_sha256") == theorem_identifier_sha256(
        "QSpecBench.Quantum.OpenQASM3.bridge_hadamard_codegen_cancel"
    )
    hh_dir = REPO / "benchmarks" / "equivalence" / "single_qubit_gate_cancellation"
    assert verify_kernel_checked_entry(entry, hh_dir) == []


def test_unitary_fragment_fail_closed_on_measurement():
    from qspecbench.qasm_matrix import UnsupportedQasmError, extract_matrix

    qasm = REPO / "benchmarks" / "algorithms" / "teleportation_preserves_state_up_to_pauli_correction" / "artifacts" / "teleportation.qasm"
    try:
        extract_matrix(qasm, extraction={"mode": "unitary_fragment"})
        raise AssertionError("expected UnsupportedQasmError")
    except UnsupportedQasmError as exc:
        assert "measurement" in str(exc).lower()


def test_teleportation_classical_control_metadata():
    spec = yaml.safe_load((TELEPORT_DIR / "spec.yaml").read_text(encoding="utf-8"))
    data = extract_matrix(
        TELEPORT_DIR / "artifacts" / "teleportation.qasm",
        extraction=spec.get("qasm_extraction"),
    )
    ctrl = [f for f in data.get("dynamic_fragments") or [] if f.get("category") == "classical_control"]
    assert ctrl == []  # teleportation uses measurement lines only in this artifact
    assert data.get("classical_control_note") is None
    assert data.get("measurement_semantics") == "projective_povm_stub"


def test_cnot_kernel_checked_manifest_chain():
    entry = next(
        e for e in load_manifest()["entries"] if e["benchmark_id"] == "cnot_self_inverse_cancellation"
    )
    assert entry.get("theorem_identifier_sha256") == theorem_identifier_sha256(
        "QSpecBench.Quantum.OpenQASM3.bridge_cnot_codegen_self_inverse"
    )
    assert verify_kernel_checked_entry(entry, CNOT_DIR) == []


def test_cnot_kernel_checked_bridge_validation():
    spec = yaml.safe_load((CNOT_DIR / "spec.yaml").read_text(encoding="utf-8"))
    bridge = json.loads((CNOT_DIR / "expected" / "semantic_bridge.json").read_text(encoding="utf-8"))
    errors = validate_kernel_checked_bridge(CNOT_DIR, bridge, spec)
    assert errors == [], errors


def test_bell_kernel_checked_manifest_chain():
    entry = next(
        e for e in load_manifest()["entries"] if e["benchmark_id"] == "bell_state_preparation"
    )
    assert entry.get("kernel_checked_theorem") == "bridge_bell_codegen_prep"
    assert entry.get("theorem_identifier_sha256") == theorem_identifier_sha256(
        "QSpecBench.Quantum.OpenQASM3.bridge_bell_codegen_prep"
    )
    assert verify_kernel_checked_entry(entry, BELL_DIR) == []


def test_bell_kernel_checked_bridge_validation():
    spec = yaml.safe_load((BELL_DIR / "spec.yaml").read_text(encoding="utf-8"))
    bridge = json.loads((BELL_DIR / "expected" / "semantic_bridge.json").read_text(encoding="utf-8"))
    errors = validate_kernel_checked_bridge(BELL_DIR, bridge, spec)
    assert errors == [], errors


def test_swap_kernel_checked_manifest_chain():
    entry = next(
        e for e in load_manifest()["entries"] if e["benchmark_id"] == "swap_from_three_cx"
    )
    assert entry.get("kernel_checked_theorem") == "bridge_swap_from_three_cx_codegen"
    assert entry.get("theorem_identifier_sha256") == theorem_identifier_sha256(
        "QSpecBench.Quantum.OpenQASM3.bridge_swap_from_three_cx_codegen"
    )
    assert verify_kernel_checked_entry(entry, SWAP_DIR) == []


def test_swap_kernel_checked_bridge_validation():
    spec = yaml.safe_load((SWAP_DIR / "spec.yaml").read_text(encoding="utf-8"))
    bridge = json.loads((SWAP_DIR / "expected" / "semantic_bridge.json").read_text(encoding="utf-8"))
    errors = validate_kernel_checked_bridge(SWAP_DIR, bridge, spec)
    assert errors == [], errors

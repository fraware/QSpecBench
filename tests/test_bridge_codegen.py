"""Tests for OpenQASM bridge codegen pilot."""

from __future__ import annotations

from pathlib import Path

from qspecbench.bridge_codegen import (
    ast_sha256,
    build_canonical_ast,
    generate_for_benchmark,
    generate_lean_stub,
    generated_lean_sha256,
    verify_manifest_codegen,
)
from qspecbench.bridge_manifest import load_manifest

REPO = Path(__file__).resolve().parents[1]
CNOT_DIR = REPO / "benchmarks" / "equivalence" / "cnot_self_inverse_cancellation"
HADAMARD_DIR = REPO / "benchmarks" / "equivalence" / "hadamard_conjugates_x_to_z"
HH_CANCEL_DIR = REPO / "benchmarks" / "equivalence" / "single_qubit_gate_cancellation"


def test_cnot_canonical_ast():
    ast = build_canonical_ast(CNOT_DIR / "artifacts" / "source.qasm")
    assert ast["n_qubits"] == 2
    assert ast["gates"] == [{"op": "cx", "qubits": [0, 1]}, {"op": "cx", "qubits": [0, 1]}]
    assert len(ast_sha256(ast)) == 64


def test_cnot_lean_stub_contains_ops():
    ast = build_canonical_ast(CNOT_DIR / "artifacts" / "source.qasm")
    lean = generate_lean_stub("cnot_self_inverse_cancellation", ast)
    assert "def ops : List QasmOp" in lean
    assert "CnotSelfInverse" in lean
    assert ".cx 0 1" in lean
    assert len(generated_lean_sha256(lean)) == 64


def test_cnot_manifest_codegen_hashes():
    entry = next(
        e for e in load_manifest()["entries"] if e["benchmark_id"] == "cnot_self_inverse_cancellation"
    )
    assert entry["ast_sha256"]
    assert entry["generated_lean_sha256"]
    errors = verify_manifest_codegen(entry, CNOT_DIR)
    assert errors == []


def test_generate_for_benchmark_writes_file():
    result = generate_for_benchmark(CNOT_DIR)
    gen_path = CNOT_DIR / result["generated_lean_path"]
    assert gen_path.is_file()
    assert result["ast_sha256"] == ast_sha256(result["ast"])


def test_hadamard_canonical_ast():
    ast = build_canonical_ast(HADAMARD_DIR / "artifacts" / "source.qasm")
    assert ast["n_qubits"] == 1
    assert ast["gates"] == [
        {"op": "h", "qubits": [0]},
        {"op": "x", "qubits": [0]},
        {"op": "h", "qubits": [0]},
    ]


def test_hadamard_manifest_codegen_hashes():
    entry = next(
        e for e in load_manifest()["entries"] if e["benchmark_id"] == "hadamard_conjugates_x_to_z"
    )
    assert entry["ast_sha256"]
    assert entry["generated_lean_sha256"]
    assert verify_manifest_codegen(entry, HADAMARD_DIR) == []


def test_clifford_target_manifest_codegen():
    from qspecbench.bridge_codegen import verify_manifest_target_codegen

    cliff = REPO / "benchmarks" / "equivalence" / "clifford_simplification_preserves_unitary"
    entry = next(
        e for e in load_manifest()["entries"]
        if e["benchmark_id"] == "clifford_simplification_preserves_unitary"
    )
    assert entry.get("target_ast_sha256")
    assert verify_manifest_target_codegen(entry, cliff) == []


def test_rx_manifest_codegen_hashes():
    rx_dir = REPO / "benchmarks" / "equivalence" / "rx_gate_equivalence_small_instance"
    entry = next(
        e for e in load_manifest()["entries"] if e["benchmark_id"] == "rx_gate_equivalence_small_instance"
    )
    assert entry["ast_sha256"]
    assert entry["generated_lean_sha256"]
    assert verify_manifest_codegen(entry, rx_dir) == []


def test_single_qubit_gate_cancellation_codegen():
    ast = build_canonical_ast(HH_CANCEL_DIR / "artifacts" / "source.qasm")
    lean = generate_lean_stub("single_qubit_gate_cancellation", ast)
    assert "single_qubit_gate_cancellation_codegen_ops" not in lean or "def ops" in lean
    assert ".gate .H 0" in lean
    entry = next(
        e for e in load_manifest()["entries"] if e["benchmark_id"] == "single_qubit_gate_cancellation"
    )
    assert verify_manifest_codegen(entry, HH_CANCEL_DIR) == []

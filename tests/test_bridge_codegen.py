"""Tests for OpenQASM bridge codegen pilot."""

from __future__ import annotations

from pathlib import Path

import pytest

from qspecbench.bridge_codegen import (
    ast_sha256,
    build_canonical_ast,
    extract_lean_theorem_statement,
    generate_for_benchmark,
    generate_lean_stub,
    generated_lean_sha256,
    OPENQASM3_LEAN,
    render_for_benchmark,
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


def test_extract_lean_theorem_statement_from_openqasm3():
    stmt = extract_lean_theorem_statement(OPENQASM3_LEAN, "bridge_cnot_codegen_self_inverse")
    assert stmt is not None
    assert "bridge_cnot_codegen_self_inverse" in stmt
    assert "Generated.CnotSelfInverse.ops" in stmt
    assert ":=" not in stmt


@pytest.mark.parametrize(
    "benchmark_id,theorem_short",
    [
        ("cnot_self_inverse_cancellation", "bridge_cnot_codegen_self_inverse"),
        ("hadamard_conjugates_x_to_z", "bridge_hadamard_codegen_conjugates_x"),
        ("single_qubit_gate_cancellation", "bridge_hadamard_codegen_cancel"),
        ("bell_state_preparation", "bridge_bell_codegen_prep"),
        ("swap_from_three_cx", "bridge_swap_from_three_cx_codegen"),
        ("toffoli_decomposition_equivalence", "bridge_toffoli_codegen_ccx"),
    ],
)
def test_kernel_bridge_theorem_extracted_from_lean(benchmark_id, theorem_short):
    from qspecbench.bridge_codegen import theorem_content_sha256

    stmt = extract_lean_theorem_statement(OPENQASM3_LEAN, theorem_short)
    assert stmt is not None, f"missing {theorem_short} in OpenQASM3.lean"
    assert theorem_content_sha256(benchmark_id)


def test_bridge_codegen_verify_is_read_only():
    import hashlib

    generated_files = list((REPO / "lean" / "QSpecBench" / "Generated").glob("*.lean"))
    witness_files = list((REPO / "benchmarks").rglob("evidence/*_codegen_ops.lean"))

    before: dict[str, tuple[float, str]] = {}
    for path in generated_files + witness_files:
        stat = path.stat()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        before[str(path)] = (stat.st_mtime_ns, digest)

    entry = next(
        e for e in load_manifest()["entries"] if e["benchmark_id"] == "cnot_self_inverse_cancellation"
    )
    assert verify_manifest_codegen(entry, CNOT_DIR) == []
    render_for_benchmark(CNOT_DIR)

    for path in generated_files + witness_files:
        stat = path.stat()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        mtime_ns, old_digest = before[str(path)]
        assert digest == old_digest, f"{path} content changed during verify/render"
        assert stat.st_mtime_ns == mtime_ns, f"{path} mtime changed during verify/render"


def test_verify_fails_on_corrupted_package_lean_without_self_healing():
    """Corrupting Generated/CnotSelfInverse.lean must fail verify and leave file corrupted."""
    from qspecbench.bridge_codegen import verify_kernel_checked_entry

    generated = REPO / "lean" / "QSpecBench" / "Generated" / "CnotSelfInverse.lean"
    original = generated.read_text(encoding="utf-8")
    corrupted = original.replace(".cx 0 1", ".cx 9 9", 1)
    assert corrupted != original
    entry = next(
        e for e in load_manifest()["entries"] if e["benchmark_id"] == "cnot_self_inverse_cancellation"
    )
    try:
        generated.write_text(corrupted, encoding="utf-8")
        errors = verify_manifest_codegen(entry, CNOT_DIR)
        errors.extend(verify_kernel_checked_entry(entry, CNOT_DIR))
        assert errors, "verify must fail when package Lean is corrupted"
        assert generated.read_text(encoding="utf-8") == corrupted
    finally:
        generated.write_text(original, encoding="utf-8")


def test_bridge_cnot_metadata_matches_manifest():
    from qspecbench.bridge_metadata import verify_bridge_cnot_metadata_against_manifest

    assert verify_bridge_cnot_metadata_against_manifest() == []


def test_theorem_source_statement_hash_alias_matches_legacy():
    from qspecbench.bridge_codegen import (
        theorem_content_sha256,
        theorem_source_statement_hash,
    )

    for bid in (
        "cnot_self_inverse_cancellation",
        "hadamard_conjugates_x_to_z",
        "single_qubit_gate_cancellation",
    ):
        assert theorem_source_statement_hash(bid) == theorem_content_sha256(bid)

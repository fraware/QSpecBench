"""Tests for OpenQASM bridge codegen pilot."""

from __future__ import annotations

from pathlib import Path

import yaml

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


def test_cnot_canonical_ast():
    ast = build_canonical_ast(CNOT_DIR / "artifacts" / "source.qasm")
    assert ast["n_qubits"] == 2
    assert ast["gates"] == [{"op": "cx", "qubits": [0, 1]}, {"op": "cx", "qubits": [0, 1]}]
    assert len(ast_sha256(ast)) == 64


def test_cnot_lean_stub_contains_ops():
    ast = build_canonical_ast(CNOT_DIR / "artifacts" / "source.qasm")
    lean = generate_lean_stub("cnot_self_inverse_cancellation", ast)
    assert "cnot_self_inverse_cancellation_codegen_ops" in lean
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

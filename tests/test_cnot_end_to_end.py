"""End-to-end CNOT kernel-checked codegen-trace chain."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from qspecbench.bridge_codegen import (
    build_canonical_ast,
    generate_for_benchmark,
    kernel_checked_theorem_name,
    theorem_content_sha256,
    theorem_identifier_sha256,
    verify_kernel_checked_entry,
    verify_manifest_codegen,
)
from qspecbench.bridge_manifest import load_manifest
from qspecbench.evidence_runner import run_evidence_checks

REPO = Path(__file__).resolve().parents[1]
CNOT_DIR = REPO / "benchmarks" / "equivalence" / "cnot_self_inverse_cancellation"
GENERATED_LEAN = REPO / "lean" / "QSpecBench" / "Generated" / "CnotSelfInverse.lean"
HAS_LAKE = shutil.which("lake") is not None or (Path.home() / ".elan" / "bin" / "lake").is_file()

pytestmark = pytest.mark.skipif(not HAS_LAKE, reason="Lean 4 / lake not installed")


def test_cnot_qasm_to_codegen_generated_module():
    ast = build_canonical_ast(CNOT_DIR / "artifacts" / "source.qasm")
    assert ast["gates"] == [{"op": "cx", "qubits": [0, 1]}, {"op": "cx", "qubits": [0, 1]}]

    result = generate_for_benchmark(CNOT_DIR)
    assert result["benchmark_id"] == "cnot_self_inverse_cancellation"
    assert Path(result["package_lean_path"]).as_posix() == "lean/QSpecBench/Generated/CnotSelfInverse.lean"
    assert GENERATED_LEAN.resolve() == (REPO / result["package_lean_path"]).resolve()
    assert GENERATED_LEAN.is_file()
    lean_text = GENERATED_LEAN.read_text(encoding="utf-8")
    assert "namespace QSpecBench.Generated.CnotSelfInverse" in lean_text
    assert ".cx 0 1" in lean_text
    evidence_copy = CNOT_DIR / result["generated_lean_path"]
    assert evidence_copy.is_file()


def test_cnot_manifest_theorem_hashes():
    entry = next(
        e for e in load_manifest()["entries"] if e["benchmark_id"] == "cnot_self_inverse_cancellation"
    )
    theorem = entry.get("kernel_checked_theorem") or entry.get("lean_theorem")
    assert theorem
    full_theorem = kernel_checked_theorem_name("cnot_self_inverse_cancellation")
    assert full_theorem
    assert entry.get("theorem_identifier_sha256") == theorem_identifier_sha256(full_theorem)
    content_hash = theorem_content_sha256("cnot_self_inverse_cancellation")
    assert content_hash
    assert entry.get("theorem_content_sha256") == content_hash
    assert verify_manifest_codegen(entry, CNOT_DIR) == []
    assert verify_kernel_checked_entry(entry, CNOT_DIR) == []


def test_cnot_evidence_compiles_and_passes_checks():
    from adapters.lean.parse_result import check

    evidence = CNOT_DIR / "evidence" / "cnot_self_inverse.lean"
    lean_result = check(evidence)
    assert lean_result["ok"], lean_result.get("errors")

    results = {r.evidence_id: r for r in run_evidence_checks(CNOT_DIR)}
    assert results["lean_cnot_proof"].ok, results["lean_cnot_proof"].errors


def test_cnot_semantic_bridge_kernel_checked_codegen_trace():
    import json

    bridge = json.loads((CNOT_DIR / "expected" / "semantic_bridge.json").read_text(encoding="utf-8"))
    assert bridge["claimed_link"] == "kernel_checked_codegen_trace"
    assert bridge.get("wire_order", {}).get("model")
    assert bridge.get("theorem_identifier_sha256")
    assert bridge.get("theorem_content_sha256")

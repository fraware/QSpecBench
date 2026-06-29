"""End-to-end CNOT kernel-checked codegen-trace chain."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from qspecbench.bridge_codegen import (
    ast_sha256,
    build_canonical_ast,
    generate_for_benchmark,
    kernel_checked_theorem_name,
    render_for_benchmark,
    theorem_content_sha256,
    theorem_identifier_sha256,
    verify_kernel_checked_entry,
    verify_manifest_codegen,
)
from qspecbench.bridge_manifest import load_manifest
from qspecbench.evidence_runner import run_evidence_checks

REPO = Path(__file__).resolve().parents[1]
CNOT_DIR = REPO / "benchmarks" / "equivalence" / "cnot_self_inverse_cancellation"
QASM_ARTIFACT = CNOT_DIR / "artifacts" / "source.qasm"
GENERATED_LEAN = REPO / "lean" / "QSpecBench" / "Generated" / "CnotSelfInverse.lean"
HAS_LAKE = shutil.which("lake") is not None or (Path.home() / ".elan" / "bin" / "lake").is_file()

pytestmark = pytest.mark.skipif(not HAS_LAKE, reason="Lean 4 / lake not installed")


def _snapshot_generated_mtimes() -> dict[str, tuple[int, str]]:
    generated_files = list((REPO / "lean" / "QSpecBench" / "Generated").glob("*.lean"))
    witness_files = list((REPO / "benchmarks").rglob("evidence/*_codegen_ops.lean"))
    before: dict[str, tuple[int, str]] = {}
    for path in generated_files + witness_files:
        stat = path.stat()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        before[str(path)] = (stat.st_mtime_ns, digest)
    return before


def _assert_read_only(before: dict[str, tuple[int, str]]) -> None:
    for path_str, (mtime_ns, old_digest) in before.items():
        path = Path(path_str)
        stat = path.stat()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == old_digest, f"{path} content changed during verify"
        assert stat.st_mtime_ns == mtime_ns, f"{path} mtime changed during verify"


def test_cnot_gold_chain_artifact_to_readonly_verify():
    """Artifact → AST → Generated module → theorem hashes → manifest → read-only verify."""
    before = _snapshot_generated_mtimes()
    artifact_bytes = QASM_ARTIFACT.read_bytes()
    artifact_sha = hashlib.sha256(artifact_bytes).hexdigest()

    ast = build_canonical_ast(QASM_ARTIFACT)
    assert ast["gates"] == [{"op": "cx", "qubits": [0, 1]}, {"op": "cx", "qubits": [0, 1]}]
    ast_hash = ast_sha256(ast)

    result = render_for_benchmark(CNOT_DIR)
    assert result["ast_sha256"] == ast_hash
    assert Path(result["package_lean_path"]).as_posix() == "lean/QSpecBench/Generated/CnotSelfInverse.lean"
    assert ".cx 0 1" in result["package_lean_text"]

    entry = next(
        e for e in load_manifest()["entries"] if e["benchmark_id"] == "cnot_self_inverse_cancellation"
    )
    full_theorem = kernel_checked_theorem_name("cnot_self_inverse_cancellation")
    assert full_theorem
    assert entry.get("theorem_identifier_sha256") == theorem_identifier_sha256(full_theorem)
    content_hash = theorem_content_sha256("cnot_self_inverse_cancellation")
    assert content_hash
    assert entry.get("theorem_content_sha256") == content_hash
    assert entry.get("ast_sha256") == ast_hash
    assert entry.get("generated_lean_sha256") == result["generated_lean_sha256"]

    bridge = json.loads((CNOT_DIR / "expected" / "semantic_bridge.json").read_text(encoding="utf-8"))
    assert bridge["claimed_link"] == "kernel_checked_codegen_trace"
    assert bridge.get("theorem_content_sha256") == content_hash

    prov = json.loads((CNOT_DIR / "expected" / "provenance.json").read_text(encoding="utf-8"))
    prov_entry = next(a for a in prov["artifacts"] if a["path"] == "artifacts/source.qasm")
    assert prov_entry["sha256"] == artifact_sha

    assert verify_manifest_codegen(entry, CNOT_DIR) == []
    assert verify_kernel_checked_entry(entry, CNOT_DIR) == []
    _assert_read_only(before)


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

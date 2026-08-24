"""Focused tests for the reference compiler and version-isolated external proof adapter."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from qspecbench.compiler_pair_codegen import GENERATED_PATH, render_compiler_pair
from qspecbench.reference_compiler import ReferenceCompilerError, compile_qasm
from qspecbench.typed_adapter_registry import get_typed_adapter

REPO = Path(__file__).resolve().parents[1]
COMPILER_BENCH = REPO / "benchmarks/equivalence/source_optimized_qasm_equivalence_small_instance"


def test_reference_compiler_reproduces_declared_target_exactly() -> None:
    source = (COMPILER_BENCH / "artifacts/source.qasm").read_text(encoding="utf-8")
    target = (COMPILER_BENCH / "artifacts/target.qasm").read_text(encoding="utf-8")
    result = compile_qasm(source)
    assert result.output == target
    assert result.transformations == ("cancel_x_pair:q[0]",)
    assert result.source_ops == (("h", 0), ("x", 0), ("x", 0))
    assert result.target_ops == (("h", 0),)
    assert result.source_sha256 == "ef022773134724a54f86931c3e90bebd416e5a0e8ccd30367433d2f59ede40d9"
    assert result.target_sha256 == "b0b1111a0363f9d90a405a33fbe23352771e64a85909ebb91758f8d82ecf6e60"


def test_reference_compiler_generated_lean_pair_is_fresh() -> None:
    assert GENERATED_PATH.read_text(encoding="utf-8") == render_compiler_pair()


def test_reference_compiler_fails_closed_on_unsupported_gate() -> None:
    source = 'OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[1] q;\nz q[0];\n'
    with pytest.raises(ReferenceCompilerError, match="unsupported executable"):
        compile_qasm(source)


def test_reference_compiler_fails_closed_on_out_of_range_qubit() -> None:
    source = 'OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[1] q;\nx q[1];\n'
    with pytest.raises(ReferenceCompilerError, match="out of range"):
        compile_qasm(source)


def _load_lean_qec_adapter_module():
    path = REPO / "adapters/lean_qec/parse_result.py"
    spec = importlib.util.spec_from_file_location("qspecbench_lean_qec_adapter", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_lean_qec_manifest_is_concrete_and_scope_limited() -> None:
    manifest_path = REPO / "adapters/lean_qec/examples/bb90_distance_10.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["upstream_commit"] == "e0b90148694cf6b9c8482b21dbd911f2d8f13493"
    assert manifest["lean_toolchain"] == "leanprover/lean4:v4.30.0-rc2"
    assert manifest["source_git_blob_sha"] == "8414ff1fb50f888998188f6e53020e95eb7891ca"
    assert manifest["theorem"] == "BB90_dist_10"
    assert manifest["supported_obligations"] == ["qec_distance_lower_bound"]
    assert "decoder_correctness" in manifest["not_supported_obligations"]
    typed = get_typed_adapter("qspecbench.lean_qec.distance.v1")
    assert typed is not None
    assert typed.implementation == "lean_qec/parse_result.py"


def test_lean_qec_adapter_default_mode_is_structured_non_claiming_skip(monkeypatch) -> None:
    monkeypatch.delenv("QSPECBENCH_LEAN_QEC_VERIFY", raising=False)
    module = _load_lean_qec_adapter_module()
    path = REPO / "adapters/lean_qec/examples/bb90_distance_10.json"
    code, payload = module.verify_manifest(path)
    assert code == 0
    assert payload["ok"] is True
    assert payload["skipped"] is True
    assert payload["supported_obligations"] == ["qec_distance_lower_bound"]
    assert payload.get("kernel_checked") is None

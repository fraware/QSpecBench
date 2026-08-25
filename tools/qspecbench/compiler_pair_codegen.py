"""Deterministic artifact-to-Lean generator for the compiler equivalence flagship.

The generated Lean module is not hand-authored evidence. It is derived from the committed source
artifact, the reference compiler's parsed IR and emitted target, and the committed target artifact.
Generation fails unless the compiler output is byte-identical to the declared target.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from qspecbench.reference_compiler import COMPILER_ID, COMPILER_VERSION, GateOp, compile_qasm
from qspecbench.schema import REPO_ROOT

BENCHMARK_ID = "source_optimized_qasm_equivalence_small_instance"
BENCHMARK_DIR = REPO_ROOT / "benchmarks" / "equivalence" / BENCHMARK_ID
SOURCE_PATH = BENCHMARK_DIR / "artifacts" / "source.qasm"
TARGET_PATH = BENCHMARK_DIR / "artifacts" / "target.qasm"
GENERATED_PATH = (
    REPO_ROOT / "lean" / "QSpecBench" / "Generated" / "SourceOptimizedCompilerPair.lean"
)


class CompilerPairCodegenError(ValueError):
    """Raised when the source/compiler/target chain is inconsistent."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _decode_utf8_lf(data: bytes, *, label: str) -> str:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CompilerPairCodegenError(f"{label} must be UTF-8: {exc}") from exc
    if "\r" in text:
        raise CompilerPairCodegenError(f"{label} must use LF line endings")
    return text


def _lean_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _lean_op(op: GateOp) -> str:
    gate, qubit = op
    if gate == "h":
        return f".gate .H {qubit}"
    if gate == "x":
        return f".gate .X {qubit}"
    raise CompilerPairCodegenError(f"unsupported compiler IR gate {gate!r}")


def _lean_ops(ops: tuple[GateOp, ...]) -> str:
    return "[" + ", ".join(_lean_op(op) for op in ops) + "]"


def _lean_string_list(items: tuple[str, ...]) -> str:
    return "[" + ", ".join(_lean_string(item) for item in items) + "]"


def render_compiler_pair() -> str:
    source_bytes = SOURCE_PATH.read_bytes()
    target_bytes = TARGET_PATH.read_bytes()
    source = _decode_utf8_lf(source_bytes, label="source artifact")
    target = _decode_utf8_lf(target_bytes, label="target artifact")

    result = compile_qasm(source)
    emitted = result.output.encode("utf-8")
    if emitted != target_bytes:
        raise CompilerPairCodegenError(
            "reference compiler output is not byte-identical to the declared target artifact"
        )

    lines = [
        "/- Generated from the compiler flagship artifacts; regenerate via compiler_pair_codegen. -/",
        "import QSpecBench.Quantum.QasmOp",
        "",
        "namespace QSpecBench.Generated.SourceOptimizedCompilerPair",
        "",
        "open QSpecBench.Quantum.QasmOp",
        "",
        f"def benchmarkId : String := {_lean_string(BENCHMARK_ID)}",
        f"def compilerId : String := {_lean_string(COMPILER_ID)}",
        f"def compilerVersion : String := {_lean_string(COMPILER_VERSION)}",
        f"def sourceSha256 : String := {_lean_string(_sha256(source_bytes))}",
        f"def targetSha256 : String := {_lean_string(_sha256(target_bytes))}",
        f"def sourceArtifact : String := {_lean_string(source)}",
        f"def targetArtifact : String := {_lean_string(target)}",
        f"def sourceOps : List QasmOp := {_lean_ops(result.source_ops)}",
        f"def targetOps : List QasmOp := {_lean_ops(result.target_ops)}",
        f"def transformationTrace : List String := {_lean_string_list(result.transformations)}",
        "",
        "end QSpecBench.Generated.SourceOptimizedCompilerPair",
        "",
    ]
    return "\n".join(lines)


def verify_generated_compiler_pair() -> list[str]:
    expected = render_compiler_pair()
    if not GENERATED_PATH.is_file():
        return [f"missing generated compiler pair: {GENERATED_PATH.relative_to(REPO_ROOT)}"]
    actual = GENERATED_PATH.read_text(encoding="utf-8")
    if actual != expected:
        return [
            "generated compiler pair is stale; regenerate "
            "lean/QSpecBench/Generated/SourceOptimizedCompilerPair.lean"
        ]
    return []


def write_generated_compiler_pair() -> Path:
    GENERATED_PATH.parent.mkdir(parents=True, exist_ok=True)
    GENERATED_PATH.write_bytes(render_compiler_pair().encode("utf-8"))
    return GENERATED_PATH


if __name__ == "__main__":
    path = write_generated_compiler_pair()
    print(path.relative_to(REPO_ROOT))

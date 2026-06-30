"""OpenQASM → canonical AST → Lean stub generator (pilot).

See docs/bridge_codegen_design.md. Emits generated ops into `lean/QSpecBench/Generated/`
and copies a witness stub into benchmark evidence for hash verification.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Any

from qspecbench.bridge_manifest import MANIFEST_PATH, compute_bridge_hashes, load_manifest
from qspecbench.denotate import ops_from_qasm_matrix
from qspecbench.qasm_matrix import extract_matrix
from qspecbench.schema import REPO_ROOT

CANONICAL_AST_VERSION = "0.1"
LEAN_GENERATED_ROOT = REPO_ROOT / "lean" / "QSpecBench" / "Generated"
OPENQASM3_LEAN = REPO_ROOT / "lean" / "QSpecBench" / "Quantum" / "OpenQASM3.lean"

_SINGLE_GATES = {"i", "x", "y", "z", "h", "s", "t", "sdg", "tdg"}

KERNEL_CHECKED_LINK = "kernel_checked_codegen_trace"
LEGACY_KERNEL_CHECKED_LINK = "kernel_checked_artifact_semantics"

GENERATED_MODULE_MAP: dict[str, str] = {
    "cnot_self_inverse_cancellation": "CnotSelfInverse",
    "hadamard_conjugates_x_to_z": "HadamardConjugatesXToZ",
    "single_qubit_gate_cancellation": "SingleQubitGateCancellation",
    "bell_state_preparation": "BellStatePreparation",
    "swap_from_three_cx": "SwapFromThreeCx",
    "toffoli_decomposition_equivalence": "ToffoliDecompositionEquivalence",
    "toffoli_decomposition_equivalence_target": "ToffoliDecompositionEquivalenceTarget",
    "circuit_identity_after_layout": "CircuitIdentityAfterLayout",
}

KERNEL_BRIDGE_IDS: frozenset[str] = frozenset(
    {
        "cnot_self_inverse_cancellation",
        "hadamard_conjugates_x_to_z",
        "single_qubit_gate_cancellation",
        "bell_state_preparation",
        "swap_from_three_cx",
        "toffoli_decomposition_equivalence",
    }
)

ARTIFACT_PARSE_THEOREM_MAP: dict[str, str] = {
    "cnot_self_inverse_cancellation": "parseQasmSource_cnot_kernel_eq_generated_ops",
    "hadamard_conjugates_x_to_z": "parseQasmSource_hxh_kernel_eq_generated_ops",
    "single_qubit_gate_cancellation": "parseQasmSource_hh_kernel_eq_generated_ops",
    "bell_state_preparation": "parseQasmSource_bell_kernel_eq_generated_ops",
    "swap_from_three_cx": "parseQasmSource_swap_kernel_eq_generated_ops",
    "toffoli_decomposition_equivalence": "parseQasmSource_toffoli_kernel_eq_generated_ops",
    "circuit_identity_after_layout": "parseQasmSource_layout_kernel_eq_generated_ops",
}

KERNEL_ARTIFACT_SOURCE_DEF: dict[str, str] = {
    "cnot_self_inverse_cancellation": "cnotKernelArtifactSource",
    "hadamard_conjugates_x_to_z": "hxhKernelArtifactSource",
    "single_qubit_gate_cancellation": "hhKernelArtifactSource",
    "bell_state_preparation": "bellKernelArtifactSource",
    "swap_from_three_cx": "swapKernelArtifactSource",
    "toffoli_decomposition_equivalence": "toffoliKernelArtifactSource",
    "circuit_identity_after_layout": "layoutKernelArtifactSource",
}

KERNEL_TARGET_ARTIFACT_SOURCE_DEF: dict[str, str] = {
    "toffoli_decomposition_equivalence": "toffoliTargetKernelArtifactSource",
}

TARGET_ARTIFACT_PARSE_THEOREM_MAP: dict[str, str] = {
    "toffoli_decomposition_equivalence": "parseQasmSource_toffoli_target_kernel_eq_generated_ops",
}

KERNEL_ARTIFACT_QASM_REL: dict[str, str] = {
    "cnot_self_inverse_cancellation": (
        "benchmarks/equivalence/cnot_self_inverse_cancellation/artifacts/source.qasm"
    ),
    "hadamard_conjugates_x_to_z": (
        "benchmarks/equivalence/hadamard_conjugates_x_to_z/artifacts/source.qasm"
    ),
    "single_qubit_gate_cancellation": (
        "benchmarks/equivalence/single_qubit_gate_cancellation/artifacts/source.qasm"
    ),
    "bell_state_preparation": "benchmarks/algorithms/bell_state_preparation/artifacts/circuit.qasm",
    "swap_from_three_cx": "benchmarks/algorithms/swap_from_three_cx/artifacts/source.qasm",
    "toffoli_decomposition_equivalence": (
        "benchmarks/equivalence/toffoli_decomposition_equivalence/artifacts/source.qasm"
    ),
}

KERNEL_TARGET_ARTIFACT_QASM_REL: dict[str, str] = {
    "toffoli_decomposition_equivalence": (
        "benchmarks/equivalence/toffoli_decomposition_equivalence/artifacts/target.qasm"
    ),
}

LEAN_AST_SHA256_FIELD = "lean_ast_sha256"
TARGET_LEAN_AST_SHA256_FIELD = "target_lean_ast_sha256"
THEOREM_ELABORATOR_TYPES_CACHE = REPO_ROOT / ".cache" / "theorem_elaborator_types.json"

# Deprecated fallback only when Lean source extraction fails (should not happen for kernel bridges).
_KERNEL_THEOREM_CONTENT_DEPRECATED: dict[str, str] = {}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_angle(angle: float) -> str | float:
    """Stable angle literal for AST hashing and Lean emission."""
    for target, label in (
        (math.pi / 2, "pi/2"),
        (math.pi / 4, "pi/4"),
        (math.pi, "pi"),
    ):
        if abs(angle - target) < 1e-9:
            return label
    return round(angle, 12)


def build_canonical_ast(
    qasm_path: Path,
    extraction: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build stable JSON AST from a QASM artifact."""
    data = extract_matrix(qasm_path, extraction=extraction)
    ops = ops_from_qasm_matrix(data)
    gates: list[dict[str, Any]] = []
    for gate, args, angle in ops:
        g = gate.lower()
        entry: dict[str, Any] = {"op": g, "qubits": list(args)}
        if angle is not None:
            entry["angle"] = _canonical_angle(angle)
        gates.append(entry)
    return {
        "canonical_ast_version": CANONICAL_AST_VERSION,
        "n_qubits": data["n_qubits"],
        "gates": gates,
    }


def ast_sha256(ast: dict[str, Any]) -> str:
    payload = json.dumps(ast, sort_keys=True, separators=(",", ":"))
    return _sha256_bytes(payload.encode("utf-8"))


def normalize_qasm_source_lf(text: str) -> str:
    """LF-normalize QASM source bytes for kernel artifact embedding."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def read_kernel_qasm_lf_normalized(qasm_path: Path) -> str:
    return normalize_qasm_source_lf(qasm_path.read_text(encoding="utf-8"))


def _is_skippable_qasm_line(line: str) -> bool:
    s = line.strip()
    if not s or s.startswith("//"):
        return True
    lower = s.lower()
    return lower.startswith(
        ("openqasm", "include", "qubit", "bit", "creg", "qreg", "barrier")
    )


def _parse_qubit_token(tok: str) -> int | None:
    t = tok.strip()
    if t.startswith("q[") and t.endswith("]"):
        return int(t[2:-1])
    if t.startswith("q") and t[1:].isdigit():
        return int(t[1:])
    return None


def lean_mirror_parse_gate_line(line: str) -> dict[str, Any] | None:
    """Mirror ``OpenQASM3Parser.parseGateLine`` gate subset for AST cross-check."""
    s = line.strip().rstrip(";").strip()
    if not s or _is_skippable_qasm_line(line):
        return None
    if s.startswith("h "):
        q = _parse_qubit_token(s[2:])
        return {"op": "h", "qubits": [q]} if q is not None else None
    if s.startswith("x "):
        q = _parse_qubit_token(s[2:])
        return {"op": "x", "qubits": [q]} if q is not None else None
    if s.startswith("t "):
        q = _parse_qubit_token(s[2:])
        return {"op": "t", "qubits": [q]} if q is not None else None
    if s.startswith("tdg "):
        q = _parse_qubit_token(s[4:])
        return {"op": "tdg", "qubits": [q]} if q is not None else None
    if s.startswith("cx ") or s.startswith("cnot "):
        rest = s.split(" ", 1)[1]
        parts = [p.strip() for p in rest.split(",")]
        if len(parts) != 2:
            return None
        c, t = _parse_qubit_token(parts[0]), _parse_qubit_token(parts[1])
        if c is None or t is None:
            return None
        return {"op": "cx", "qubits": [c, t]}
    if s.startswith("ccx "):
        rest = s.split(" ", 1)[1]
        parts = [p.strip() for p in rest.split(",")]
        if len(parts) != 3:
            return None
        c0, c1, t = (
            _parse_qubit_token(parts[0]),
            _parse_qubit_token(parts[1]),
            _parse_qubit_token(parts[2]),
        )
        if c0 is None or c1 is None or t is None:
            return None
        return {"op": "ccx", "qubits": [c0, c1, t]}
    return None


def build_lean_mirror_canonical_ast(qasm_path: Path) -> dict[str, Any]:
    """Build canonical AST JSON mirroring Lean ``parseQasmSource`` gate list."""
    gates: list[dict[str, Any]] = []
    for raw in read_kernel_qasm_lf_normalized(qasm_path).splitlines():
        entry = lean_mirror_parse_gate_line(raw)
        if entry is not None:
            gates.append({"op": entry["op"], "qubits": list(entry["qubits"])})
    max_q = max((q for g in gates for q in g["qubits"]), default=-1)
    return {
        "canonical_ast_version": CANONICAL_AST_VERSION,
        "n_qubits": max_q + 1,
        "gates": gates,
    }


def lean_ast_sha256_from_qasm(qasm_path: Path) -> str:
    return ast_sha256(build_lean_mirror_canonical_ast(qasm_path))


def lean_ast_sha256_for_benchmark(benchmark_id: str) -> str | None:
    rel = KERNEL_ARTIFACT_QASM_REL.get(benchmark_id)
    if not rel:
        return None
    return lean_ast_sha256_from_qasm(REPO_ROOT / rel)


def target_lean_ast_sha256_for_benchmark(benchmark_id: str) -> str | None:
    rel = KERNEL_TARGET_ARTIFACT_QASM_REL.get(benchmark_id)
    if not rel:
        return None
    return lean_ast_sha256_from_qasm(REPO_ROOT / rel)


def to_lean_string_literal(source: str) -> str:
    escaped = (
        source.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
    )
    return f'  "{escaped}"'


def update_lean_kernel_artifact_source_def(
    def_name: str,
    source: str,
    *,
    path: Path | None = None,
) -> bool:
    """Replace ``def {def_name} : String :=`` literal; return True if changed."""
    lean_path = path or (REPO_ROOT / "lean" / "QSpecBench" / "Quantum" / "OpenQASM3Parser.lean")
    text = lean_path.read_text(encoding="utf-8")
    pattern = rf'(def {re.escape(def_name)} : String :=\s*\n)(  "(?:[^"\\]|\\.)*")'
    replacement = rf"\g<1>{to_lean_string_literal(source)}"
    new_text, count = re.subn(pattern, replacement, text, count=1)
    if count == 0:
        raise ValueError(f"{def_name} not found in {lean_path}")
    if new_text == text:
        return False
    lean_path.write_text(new_text, encoding="utf-8")
    return True


def _lean_single_gate(gate: str) -> str:
    g = gate.lower()
    mapping = {
        "i": "I",
        "x": "X",
        "y": "Y",
        "z": "Z",
        "h": "H",
        "s": "S",
        "t": "T",
        "sdg": "Sdg",
        "tdg": "Tdg",
    }
    if g not in mapping:
        raise ValueError(f"unsupported single-qubit gate for codegen: {gate!r}")
    return mapping[g]


def _lean_angle_literal(angle: str | float) -> str:
    if angle == "pi/2":
        return "(Real.pi / 2)"
    if angle == "pi/4":
        return "(Real.pi / 4)"
    if angle == "pi":
        return "Real.pi"
    if isinstance(angle, (int, float)):
        return str(angle)
    raise ValueError(f"unsupported angle literal: {angle!r}")


def _lean_op_item(entry: dict[str, Any]) -> str:
    op = entry["op"].lower()
    qubits = entry["qubits"]
    if op in {"cx", "cnot"}:
        if len(qubits) != 2:
            raise ValueError(f"cx expects two qubits, got {qubits!r}")
        return f".cx {qubits[0]} {qubits[1]}"
    if op == "ccx":
        if len(qubits) != 3:
            raise ValueError(f"ccx expects three qubits, got {qubits!r}")
        return f".ccx {qubits[0]} {qubits[1]} {qubits[2]}"
    if op == "swap":
        if len(qubits) != 2:
            raise ValueError(f"swap expects two qubits, got {qubits!r}")
        return f".swap {qubits[0]} {qubits[1]}"
    if op == "rx":
        if len(qubits) != 1:
            raise ValueError(f"rx expects one qubit, got {qubits!r}")
        angle = entry.get("angle")
        if angle is None:
            raise ValueError("rx gate requires angle in canonical AST")
        return f".rx {_lean_angle_literal(angle)} {qubits[0]}"
    if op in _SINGLE_GATES:
        if len(qubits) != 1:
            raise ValueError(f"{op} expects one qubit, got {qubits!r}")
        return f".gate .{_lean_single_gate(op)} {qubits[0]}"
    raise ValueError(f"unsupported gate for Lean codegen: {op!r}")


def generated_module_name(benchmark_id: str) -> str | None:
    return GENERATED_MODULE_MAP.get(benchmark_id)


def package_lean_path(benchmark_id: str) -> Path | None:
    name = generated_module_name(benchmark_id)
    if not name:
        return None
    return LEAN_GENERATED_ROOT / f"{name}.lean"


def generate_lean_stub(
    benchmark_id: str,
    ast: dict[str, Any],
    *,
    witness: bool = False,
) -> str:
    """Emit Lean declaring `ops : List QasmOp` in QSpecBench.Generated.*."""
    module_name = generated_module_name(benchmark_id)
    if module_name is None:
        safe_id = re.sub(r"[^a-zA-Z0-9_]", "_", benchmark_id)
        ops_name = f"{safe_id}_codegen_ops"
        items = ", ".join(_lean_op_item(g) for g in ast["gates"])
        return (
            "/- QSpecBench bridge codegen (pilot): regenerate via "
            "`qspecbench bridge-codegen generate`. -/\n"
            "import QSpecBench.Quantum.QasmOp\n\n"
            f"open QSpecBench.Quantum.QasmOp\n\n"
            f"def {ops_name} : List QasmOp := [{items}]\n"
        )

    items = ", ".join(_lean_op_item(g) for g in ast["gates"])
    header = (
        "/- QSpecBench bridge codegen: regenerate via `qspecbench bridge-codegen generate`. -/\n"
        if not witness
        else (
            "/- QSpecBench bridge codegen witness (hash must match package stub). -/\n"
            f"/- benchmark_id = {benchmark_id!r} -/\n"
        )
    )
    return (
        f"{header}"
        "import QSpecBench.Quantum.QasmOp\n\n"
        f"namespace QSpecBench.Generated.{module_name}\n\n"
        "open QSpecBench.Quantum.QasmOp\n\n"
        f"def ops : List QasmOp := [{items}]\n\n"
        f"end QSpecBench.Generated.{module_name}\n"
    )


def generated_lean_sha256(text: str) -> str:
    normalized = text.replace("\r\n", "\n").encode("utf-8")
    return _sha256_bytes(normalized)


def theorem_identifier_sha256(full_theorem: str) -> str:
    """Stable hash of the kernel-checked theorem identifier (module + name)."""
    payload = json.dumps(
        {"theorem": full_theorem, "kind": KERNEL_CHECKED_LINK},
        sort_keys=True,
        separators=(",", ":"),
    )
    return _sha256_bytes(payload.encode("utf-8"))


def theorem_sha256(full_theorem: str) -> str:
    """Deprecated alias for theorem_identifier_sha256."""
    return theorem_identifier_sha256(full_theorem)


def _normalize_theorem_statement(text: str) -> str:
    return " ".join(text.split())


def extract_lean_theorem_statement(path: Path, theorem_name: str) -> str | None:
    """Parse `theorem name ... :=` from a Lean file (statement only, before proof)."""
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"\btheorem\s+{re.escape(theorem_name)}\b", text)
    if not match:
        return None
    rest = text[match.start() :]
    assign = rest.find(":=")
    if assign < 0:
        return None
    return _normalize_theorem_statement(rest[:assign])


THEOREM_SOURCE_HASH_FIELD = "theorem_source_statement_hash"
THEOREM_SOURCE_HASH_FIELD_LEGACY = "theorem_content_sha256"


def theorem_source_statement_hash_from_parts(
    statement: str, module_text: str | None = None
) -> str:
    """Hash syntactic Lean theorem statement extraction (not elaborator export)."""
    payload: dict[str, Any] = {
        "theorem_content": _normalize_theorem_statement(statement),
        "kind": KERNEL_CHECKED_LINK,
    }
    if module_text is not None:
        payload["generated_module_sha256"] = generated_lean_sha256(module_text)
    return _sha256_bytes(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def theorem_content_sha256_from_parts(statement: str, module_text: str | None = None) -> str:
    """Deprecated alias for ``theorem_source_statement_hash_from_parts``."""
    return theorem_source_statement_hash_from_parts(statement, module_text)


def _canonicalize_module_refs(text: str) -> str:
    return text.replace("QSpecBench.Generated.", "Generated.")


def theorem_source_statement_hash(benchmark_id: str) -> str | None:
    """Stable hash of kernel theorem statement from syntactic Lean source extraction."""
    theorem_full = kernel_checked_theorem_name(benchmark_id)
    if not theorem_full:
        return None
    theorem_short = theorem_full.split(".")[-1]
    extracted = extract_lean_theorem_statement(OPENQASM3_LEAN, theorem_short)
    if benchmark_id in GENERATED_MODULE_MAP:
        if not extracted:
            raise ValueError(
                f"kernel bridge {benchmark_id!r} missing theorem {theorem_short!r} "
                f"in {OPENQASM3_LEAN.relative_to(REPO_ROOT)}"
            )
        deprecated = _KERNEL_THEOREM_CONTENT_DEPRECATED.get(benchmark_id)
        if deprecated:
            canon_dep = _canonicalize_module_refs(_normalize_theorem_statement(deprecated))
            if canon_dep != extracted:
                raise ValueError(
                    f"_KERNEL_THEOREM_CONTENT_DEPRECATED drift for {benchmark_id!r}: "
                    "update deprecated map or Lean source"
                )
    statement = extracted or _KERNEL_THEOREM_CONTENT_DEPRECATED.get(benchmark_id)
    if not statement:
        return None
    package_path = package_lean_path(benchmark_id)
    module_text = (
        package_path.read_text(encoding="utf-8") if package_path and package_path.is_file() else None
    )
    return theorem_source_statement_hash_from_parts(statement, module_text)


def theorem_content_sha256(benchmark_id: str) -> str | None:
    """Deprecated alias for ``theorem_source_statement_hash`` (legacy manifest field name)."""
    return theorem_source_statement_hash(benchmark_id)


def read_theorem_source_hash(record: dict[str, Any]) -> str | None:
    """Read canonical or legacy theorem statement hash from manifest/bridge JSON."""
    canonical = record.get(THEOREM_SOURCE_HASH_FIELD)
    legacy = record.get(THEOREM_SOURCE_HASH_FIELD_LEGACY)
    if canonical and legacy and canonical != legacy:
        return None
    return canonical or legacy


def sync_theorem_source_hash_fields(record: dict[str, Any], expected: str | None) -> None:
    """Ensure manifest/bridge records carry both hash field names when expected is known."""
    if not expected:
        return
    record[THEOREM_SOURCE_HASH_FIELD] = expected
    record[THEOREM_SOURCE_HASH_FIELD_LEGACY] = expected


KERNEL_CHECKED_THEOREMS: dict[str, str] = {
    "cnot_self_inverse_cancellation": "QSpecBench.Quantum.OpenQASM3.bridge_cnot_codegen_self_inverse",
    "hadamard_conjugates_x_to_z": "QSpecBench.Quantum.OpenQASM3.bridge_hadamard_codegen_conjugates_x",
    "single_qubit_gate_cancellation": "QSpecBench.Quantum.OpenQASM3.bridge_hadamard_codegen_cancel",
    "bell_state_preparation": "QSpecBench.Quantum.OpenQASM3.bridge_bell_codegen_prep",
    "swap_from_three_cx": "QSpecBench.Quantum.OpenQASM3.bridge_swap_from_three_cx_codegen",
    "toffoli_decomposition_equivalence": "QSpecBench.Quantum.OpenQASM3.bridge_toffoli_codegen_ccx",
    "circuit_identity_after_layout": "QSpecBench.Quantum.OpenQASM3.bridge_circuit_identity_after_layout_codegen",
}

KERNEL_ARTIFACT_PARSE_THEOREMS = ARTIFACT_PARSE_THEOREM_MAP
LEAN_KERNEL_ARTIFACT_SOURCE_DEFS = KERNEL_ARTIFACT_SOURCE_DEF

OPENQASM3_PARSER_LEAN = REPO_ROOT / "lean" / "QSpecBench" / "Quantum" / "OpenQASM3Parser.lean"

THEOREM_ELABORATOR_HASH_FIELD = "theorem_elaborator_hash"


def kernel_checked_theorem_name(benchmark_id: str) -> str | None:
    return KERNEL_CHECKED_THEOREMS.get(benchmark_id)


def kernel_artifact_parse_theorem(benchmark_id: str) -> str | None:
    return ARTIFACT_PARSE_THEOREM_MAP.get(benchmark_id)


def extract_lean_kernel_artifact_source(def_name: str, path: Path = OPENQASM3_PARSER_LEAN) -> str:
    """Read embedded Lean ``*KernelArtifactSource`` string literal."""
    text = path.read_text(encoding="utf-8")
    match = re.search(
        rf'def {re.escape(def_name)} : String :=\s*\n\s*"((?:[^"\\]|\\.)*)"',
        text,
    )
    if not match:
        raise ValueError(f"{def_name} not found in {path}")
    return bytes(match.group(1), "utf-8").decode("unicode_escape")


def lean_kernel_artifact_source_bytes(benchmark_id: str) -> bytes:
    def_name = KERNEL_ARTIFACT_SOURCE_DEF.get(benchmark_id)
    if not def_name:
        raise KeyError(benchmark_id)
    return extract_lean_kernel_artifact_source(def_name).encode("utf-8")


def extract_lean_theorem_type(path: Path, theorem_name: str) -> str | None:
    """Parse type signature from ``theorem name ... : TYPE :=`` (regex fallback)."""
    statement = extract_lean_theorem_statement(path, theorem_name)
    if not statement:
        return None
    colon_idx = statement.rfind(":")
    if colon_idx < 0:
        return None
    return _normalize_theorem_statement(statement[colon_idx + 1 :])


@lru_cache(maxsize=1)
def _elaborator_exported_types() -> dict[str, str]:
    """Load elaborator types from cache or ``lake exe exportTheoremTypes`` when enabled."""
    if THEOREM_ELABORATOR_TYPES_CACHE.is_file():
        try:
            payload = json.loads(THEOREM_ELABORATOR_TYPES_CACHE.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return {
                    str(k): _normalize_theorem_statement(str(v))
                    for k, v in payload.items()
                    if v
                }
        except (json.JSONDecodeError, OSError, TypeError):
            pass
    if os.environ.get("QSPECBENCH_LEAN_ELABORATOR", "").strip() not in {"1", "true", "yes"}:
        return {}
    lean_dir = REPO_ROOT / "lean"
    if not (lean_dir / "lakefile.lean").is_file():
        return {}
    try:
        proc = subprocess.run(
            ["lake", "exe", "exportTheoremTypes"],
            cwd=lean_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=120,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return {}
    if proc.returncode != 0:
        return {}
    out: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if "\t" not in line:
            continue
        bid, ty = line.split("\t", 1)
        out[bid.strip()] = _normalize_theorem_statement(ty.strip())
    if out:
        THEOREM_ELABORATOR_TYPES_CACHE.parent.mkdir(parents=True, exist_ok=True)
        THEOREM_ELABORATOR_TYPES_CACHE.write_text(
            json.dumps(out, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return out


def write_elaborator_types_cache(types: dict[str, str]) -> None:
    THEOREM_ELABORATOR_TYPES_CACHE.parent.mkdir(parents=True, exist_ok=True)
    THEOREM_ELABORATOR_TYPES_CACHE.write_text(
        json.dumps(types, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _elaborator_exported_types.cache_clear()


def theorem_elaborator_type(benchmark_id: str) -> str | None:
    """Normalized theorem type from Lean elaborator export, else regex fallback."""
    exported = _elaborator_exported_types()
    if benchmark_id in exported:
        return exported[benchmark_id]
    theorem_full = kernel_checked_theorem_name(benchmark_id)
    if not theorem_full:
        return None
    return extract_lean_theorem_type(OPENQASM3_LEAN, theorem_full.split(".")[-1])


def theorem_elaborator_hash(benchmark_id: str) -> str | None:
    """Hash normalized theorem type (elaborator export primary; regex secondary)."""
    type_sig = theorem_elaborator_type(benchmark_id)
    if not type_sig:
        return None
    kind = (
        "theorem_elaborator_hash_v1"
        if benchmark_id in _elaborator_exported_types()
        else "theorem_elaborator_hash_v0"
    )
    payload = {
        "benchmark_id": benchmark_id,
        "kind": kind,
        "theorem_type": type_sig,
    }
    return _sha256_bytes(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def codegen_output_path(claim_dir: Path, benchmark_id: str) -> Path:
    safe_id = re.sub(r"[^a-zA-Z0-9_]", "_", benchmark_id)
    return claim_dir / "evidence" / f"{safe_id}_codegen_ops.lean"


def _resolve_qasm_artifact(
    claim_dir: Path,
    spec: dict[str, Any],
    *,
    qasm_role: str,
) -> tuple[str, Path]:
    benchmark_id = spec.get("id", claim_dir.name)
    bridge_path = claim_dir / "expected" / "semantic_bridge.json"
    qasm_rel: str | None = None
    if bridge_path.is_file():
        bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
        if qasm_role == "target":
            qasm_rel = bridge.get("target_qasm_artifact")
        else:
            qasm_rel = bridge.get("qasm_artifact")
    if not qasm_rel:
        for obj in spec.get("objects", []):
            if obj.get("format") == "qasm3" and obj.get("role") == qasm_role:
                qasm_rel = obj.get("path")
                break
    if not qasm_rel and qasm_role == "source":
        for obj in spec.get("objects", []):
            if obj.get("format") == "qasm3" and obj.get("role") == "source":
                qasm_rel = obj.get("path")
                break
    if not qasm_rel:
        raise FileNotFoundError(f"no qasm3 {qasm_role} artifact for {benchmark_id}")
    return qasm_rel, claim_dir / qasm_rel


def render_for_benchmark(claim_dir: Path, *, qasm_role: str = "source") -> dict[str, Any]:
    """Pure render: AST, witness/package Lean text, hashes — no filesystem writes."""
    import yaml

    spec_path = claim_dir / "spec.yaml"
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    benchmark_id = spec.get("id", claim_dir.name)
    extraction = spec.get("qasm_extraction")
    qasm_rel, qasm_path = _resolve_qasm_artifact(claim_dir, spec, qasm_role=qasm_role)

    ast = build_canonical_ast(qasm_path, extraction=extraction)
    stub_id = benchmark_id if qasm_role == "source" else f"{benchmark_id}_target"
    witness_text = generate_lean_stub(stub_id, ast, witness=True)
    package_path = package_lean_path(stub_id)
    package_text: str | None = None
    package_rel: str | None = None
    if package_path is not None:
        package_text = generate_lean_stub(stub_id, ast, witness=False)
        package_rel = str(package_path.relative_to(REPO_ROOT))

    artifact_sha, trace_sha, _trace = compute_bridge_hashes(qasm_path, extraction=extraction)
    return {
        "benchmark_id": benchmark_id,
        "stub_id": stub_id,
        "qasm_role": qasm_role,
        "qasm_artifact": qasm_rel,
        "artifact_sha256": artifact_sha,
        "gate_trace_sha256": trace_sha,
        "ast": ast,
        "ast_sha256": ast_sha256(ast),
        "lean_ast_sha256": lean_ast_sha256_from_qasm(qasm_path),
        "witness_lean_text": witness_text,
        "package_lean_text": package_text,
        "generated_lean_path": str(codegen_output_path(claim_dir, stub_id).relative_to(claim_dir)),
        "generated_lean_sha256": generated_lean_sha256(witness_text),
        "package_lean_path": package_rel,
        "package_lean_sha256": generated_lean_sha256(package_text) if package_text else None,
    }


def write_generated_outputs(claim_dir: Path, result: dict[str, Any]) -> None:
    """Write witness and package Lean files from a render_for_benchmark result."""
    out_path = claim_dir / result["generated_lean_path"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(result["witness_lean_text"], encoding="utf-8")

    package_rel = result.get("package_lean_path")
    package_text = result.get("package_lean_text")
    if package_rel and package_text:
        package_path = REPO_ROOT / package_rel
        package_path.parent.mkdir(parents=True, exist_ok=True)
        package_path.write_text(package_text, encoding="utf-8")


def generate_for_benchmark(claim_dir: Path, *, qasm_role: str = "source") -> dict[str, Any]:
    """Generate Lean stub + hashes for one benchmark (source or target QASM)."""
    result = render_for_benchmark(claim_dir, qasm_role=qasm_role)
    write_generated_outputs(claim_dir, result)
    return result


def verify_manifest_target_codegen(entry: dict[str, Any], claim_dir: Path) -> list[str]:
    """Verify target-side ast_sha256 and generated_lean_sha256 when present."""
    errors: list[str] = []
    benchmark_id = entry.get("benchmark_id", "")
    if not entry.get("target_ast_sha256") and not entry.get("target_generated_lean_sha256"):
        return errors
    try:
        result = render_for_benchmark(claim_dir, qasm_role="target")
    except (FileNotFoundError, ValueError) as exc:
        return [f"target codegen verify failed for {benchmark_id}: {exc}"]
    if entry.get("target_ast_sha256") and entry["target_ast_sha256"] != result["ast_sha256"]:
        errors.append(f"target_ast_sha256 drift for {benchmark_id}")
    if entry.get("target_generated_lean_sha256"):
        if entry["target_generated_lean_sha256"] != result["generated_lean_sha256"]:
            errors.append(f"target_generated_lean_sha256 drift for {benchmark_id}")
        gen_path = claim_dir / result["generated_lean_path"]
        if gen_path.is_file():
            on_disk = generated_lean_sha256(gen_path.read_text(encoding="utf-8"))
            if on_disk != entry["target_generated_lean_sha256"]:
                errors.append(
                    f"target generated Lean file hash mismatch for {benchmark_id}: "
                    f"{result['generated_lean_path']}"
                )
    return errors


def verify_manifest_codegen(entry: dict[str, Any], claim_dir: Path) -> list[str]:
    """Verify ast_sha256 and generated_lean_sha256 for a manifest entry."""
    errors: list[str] = []
    benchmark_id = entry.get("benchmark_id", "")
    if not entry.get("ast_sha256") and not entry.get("generated_lean_sha256"):
        return errors

    try:
        result = render_for_benchmark(claim_dir)
    except (FileNotFoundError, ValueError) as exc:
        return [f"codegen verify failed for {benchmark_id}: {exc}"]

    if entry.get("ast_sha256") and entry["ast_sha256"] != result["ast_sha256"]:
        errors.append(
            f"ast_sha256 drift for {benchmark_id}: manifest != regenerated canonical AST"
        )
    if entry.get("lean_ast_sha256") and result.get("lean_ast_sha256"):
        if entry["lean_ast_sha256"] != result["lean_ast_sha256"]:
            errors.append(f"lean_ast_sha256 drift for {benchmark_id}")
        if entry.get("ast_sha256") and entry["lean_ast_sha256"] != entry["ast_sha256"]:
            errors.append(
                f"lean_ast_sha256 != ast_sha256 for {benchmark_id} "
                "(Python extractor vs Lean mirror parseQasmSource gate list)"
            )
    if entry.get("generated_lean_sha256"):
        if entry["generated_lean_sha256"] != result["generated_lean_sha256"]:
            errors.append(
                f"generated_lean_sha256 drift for {benchmark_id}: "
                "manifest != regenerated Lean stub"
            )
        gen_path = claim_dir / result["generated_lean_path"]
        if gen_path.is_file():
            on_disk = generated_lean_sha256(gen_path.read_text(encoding="utf-8"))
            if on_disk != entry["generated_lean_sha256"]:
                errors.append(
                    f"generated Lean file hash mismatch for {benchmark_id}: "
                    f"{result['generated_lean_path']}"
                )
    if entry.get("package_lean_sha256") and result.get("package_lean_sha256"):
        if entry["package_lean_sha256"] != result["package_lean_sha256"]:
            errors.append(f"package_lean_sha256 drift for {benchmark_id}")
    package_path = package_lean_path(benchmark_id)
    if entry.get("package_lean_sha256") and package_path and package_path.is_file():
        on_disk_pkg = generated_lean_sha256(package_path.read_text(encoding="utf-8"))
        if on_disk_pkg != entry["package_lean_sha256"]:
            errors.append(
                f"on-disk package Lean hash mismatch for {benchmark_id}: "
                f"{package_path.relative_to(REPO_ROOT)}"
            )
    errors.extend(verify_manifest_target_codegen(entry, claim_dir))
    return errors


def update_manifest_entry(benchmark_id: str, result: dict[str, Any]) -> None:
    """Write codegen hashes into bridge_theorem_manifest.json."""
    manifest = load_manifest()
    updated = False
    kernel_theorem = kernel_checked_theorem_name(benchmark_id)
    for entry in manifest.get("entries", []):
        if entry.get("benchmark_id") != benchmark_id:
            continue
        entry["ast_sha256"] = result["ast_sha256"]
        entry["generated_lean_sha256"] = result["generated_lean_sha256"]
        if result.get("package_lean_sha256"):
            entry["package_lean_sha256"] = result["package_lean_sha256"]
        entry["obligation_ids"] = entry.get("obligation_ids") or ["semantic_bridge"]
        if kernel_theorem:
            entry["kernel_checked_theorem"] = kernel_theorem.split(".")[-1]
            entry["theorem_identifier_sha256"] = theorem_identifier_sha256(kernel_theorem)
            entry["theorem_sha256"] = entry["theorem_identifier_sha256"]
            content_hash = theorem_source_statement_hash(benchmark_id)
            if content_hash:
                sync_theorem_source_hash_fields(entry, content_hash)
        updated = True
        break
    if not updated:
        raise KeyError(f"benchmark_id {benchmark_id!r} not in {MANIFEST_PATH}")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def normalize_claimed_link(claimed_link: str | None) -> str | None:
    if claimed_link == LEGACY_KERNEL_CHECKED_LINK:
        return KERNEL_CHECKED_LINK
    return claimed_link


def is_kernel_checked_link(claimed_link: str | None) -> bool:
    return claimed_link in {KERNEL_CHECKED_LINK, LEGACY_KERNEL_CHECKED_LINK}


def verify_kernel_checked_entry(entry: dict[str, Any], claim_dir: Path) -> list[str]:
    """Verify full codegen-trace chain for kernel_checked bridges."""
    errors = verify_manifest_codegen(entry, claim_dir)
    benchmark_id = entry.get("benchmark_id", "")
    expected_theorem = kernel_checked_theorem_name(benchmark_id)
    if not expected_theorem:
        errors.append(f"no kernel_checked_theorem mapping for {benchmark_id!r}")
        return errors
    if entry.get("kernel_checked_theorem") != expected_theorem.split(".")[-1]:
        errors.append(
            f"kernel_checked_theorem mismatch for {benchmark_id}: "
            f"manifest {entry.get('kernel_checked_theorem')!r} != "
            f"{expected_theorem.split('.')[-1]!r}"
        )
    expected_id_hash = theorem_identifier_sha256(expected_theorem)
    stored_id = entry.get("theorem_identifier_sha256") or entry.get("theorem_sha256")
    if stored_id and stored_id != expected_id_hash:
        errors.append(f"theorem_identifier_sha256 drift for {benchmark_id}")
    expected_content = theorem_source_statement_hash(benchmark_id)
    stored_content = read_theorem_source_hash(entry)
    expected_elab = theorem_elaborator_hash(benchmark_id)
    stored_elab = entry.get(THEOREM_ELABORATOR_HASH_FIELD)
    if expected_elab:
        if not stored_elab:
            errors.append(
                f"{KERNEL_CHECKED_LINK} requires {THEOREM_ELABORATOR_HASH_FIELD} for {benchmark_id}"
            )
        elif stored_elab != expected_elab:
            errors.append(f"{THEOREM_ELABORATOR_HASH_FIELD} drift for {benchmark_id}")
    if expected_content and stored_content:
        if stored_content != expected_content:
            errors.append(f"theorem_source_statement_hash drift for {benchmark_id}")
        if (
            entry.get(THEOREM_SOURCE_HASH_FIELD)
            and entry.get(THEOREM_SOURCE_HASH_FIELD_LEGACY)
            and entry[THEOREM_SOURCE_HASH_FIELD] != entry[THEOREM_SOURCE_HASH_FIELD_LEGACY]
        ):
            errors.append(
                f"theorem_source_statement_hash and theorem_content_sha256 disagree for {benchmark_id}"
            )
    if not entry.get("ast_sha256") or not entry.get("generated_lean_sha256"):
        errors.append(
            f"{KERNEL_CHECKED_LINK} requires ast_sha256 and generated_lean_sha256 for {benchmark_id}"
        )
    if not stored_id:
        errors.append(f"{KERNEL_CHECKED_LINK} requires theorem_identifier_sha256 for {benchmark_id}")
    if expected_content and not stored_content:
        errors.append(
            f"{KERNEL_CHECKED_LINK} requires theorem_source_statement_hash for {benchmark_id}"
        )
    if benchmark_id in KERNEL_BRIDGE_IDS:
        expected_lean_ast = lean_ast_sha256_for_benchmark(benchmark_id)
        if expected_lean_ast and entry.get("lean_ast_sha256") != expected_lean_ast:
            errors.append(f"lean_ast_sha256 manifest drift for {benchmark_id}")
        if (
            entry.get("lean_ast_sha256")
            and entry.get("ast_sha256")
            and entry["lean_ast_sha256"] != entry["ast_sha256"]
        ):
            errors.append(
                f"lean_ast_sha256 != ast_sha256 in manifest for {benchmark_id}"
            )
    if not generated_module_name(benchmark_id):
        errors.append(f"kernel bridge {benchmark_id} missing generated module mapping")
    return errors


def verify_kernel_artifact_semantics_bridge(bridge: dict[str, Any], benchmark_id: str) -> list[str]:
    """Require Lean parse theorem reference for kernel_checked_artifact_semantics."""
    errors: list[str] = []
    if bridge.get("claimed_link") != LEGACY_KERNEL_CHECKED_LINK:
        return errors
    parse_thm = bridge.get("artifact_parse_theorem")
    expected = kernel_artifact_parse_theorem(benchmark_id)
    if not expected:
        errors.append(f"no artifact parse theorem mapping for {benchmark_id!r}")
        return errors
    if not parse_thm:
        errors.append(
            f"artifact_parse_theorem is required for {LEGACY_KERNEL_CHECKED_LINK} ({benchmark_id})"
        )
    elif parse_thm != expected:
        errors.append(
            f"artifact_parse_theorem must be {expected!r}, got {parse_thm!r}"
        )
    parser_lean = OPENQASM3_PARSER_LEAN
    openqasm3_lean = OPENQASM3_LEAN
    if parser_lean.is_file() and parse_thm:
        text = parser_lean.read_text(encoding="utf-8")
        if f"theorem {parse_thm}" not in text:
            errors.append(f"Lean parse theorem {parse_thm!r} not found in OpenQASM3Parser.lean")
    elaborator = bridge.get(THEOREM_ELABORATOR_HASH_FIELD)
    expected_elab = theorem_elaborator_hash(benchmark_id)
    if expected_elab:
        if not elaborator:
            errors.append(
                f"{THEOREM_ELABORATOR_HASH_FIELD} required for {LEGACY_KERNEL_CHECKED_LINK} "
                f"({benchmark_id})"
            )
        elif elaborator != expected_elab:
            errors.append(f"{THEOREM_ELABORATOR_HASH_FIELD} drift for {benchmark_id}")
    source_hash = bridge.get(THEOREM_SOURCE_HASH_FIELD) or bridge.get("theorem_content_sha256")
    expected_source = theorem_source_statement_hash(benchmark_id)
    if expected_source and source_hash and source_hash != expected_source:
        errors.append(f"theorem_source_statement_hash secondary drift for {benchmark_id}")
    if benchmark_id in KERNEL_BRIDGE_IDS:
        lean_ast = bridge.get(LEAN_AST_SHA256_FIELD)
        expected_lean_ast = lean_ast_sha256_for_benchmark(benchmark_id)
        if expected_lean_ast:
            if not lean_ast:
                errors.append(f"{LEAN_AST_SHA256_FIELD} required for kernel bridge {benchmark_id}")
            elif lean_ast != expected_lean_ast:
                errors.append(f"{LEAN_AST_SHA256_FIELD} drift for {benchmark_id}")
            ast = bridge.get("ast_sha256")
            if ast and lean_ast and lean_ast != ast:
                errors.append(
                    f"{LEAN_AST_SHA256_FIELD} != ast_sha256 in semantic_bridge for {benchmark_id}"
                )
    wire_thm = bridge.get("wire_order_bridge_theorem")
    if wire_thm:
        found = False
        for lean_path in (parser_lean, openqasm3_lean):
            if lean_path.is_file():
                text = lean_path.read_text(encoding="utf-8")
                if f"theorem {wire_thm}" in text or f"lemma {wire_thm}" in text:
                    found = True
                    break
        if not found:
            errors.append(
                f"wire_order_bridge_theorem {wire_thm!r} not found in OpenQASM3.lean "
                "or OpenQASM3Parser.lean"
            )
    return errors

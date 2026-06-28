"""OpenQASM → canonical AST → Lean stub generator (pilot).

See docs/bridge_codegen_design.md. Emits generated ops into `lean/QSpecBench/Generated/`
and copies a witness stub into benchmark evidence for hash verification.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

from qspecbench.bridge_manifest import MANIFEST_PATH, compute_bridge_hashes, load_manifest
from qspecbench.denotate import ops_from_qasm_matrix
from qspecbench.qasm_matrix import extract_matrix
from qspecbench.schema import REPO_ROOT

CANONICAL_AST_VERSION = "0.1"
LEAN_GENERATED_ROOT = REPO_ROOT / "lean" / "QSpecBench" / "Generated"

_SINGLE_GATES = {"i", "x", "y", "z", "h", "s", "t", "sdg", "tdg"}

KERNEL_CHECKED_LINK = "kernel_checked_codegen_trace"
LEGACY_KERNEL_CHECKED_LINK = "kernel_checked_artifact_semantics"

GENERATED_MODULE_MAP: dict[str, str] = {
    "cnot_self_inverse_cancellation": "CnotSelfInverse",
    "hadamard_conjugates_x_to_z": "HadamardConjugatesXToZ",
    "single_qubit_gate_cancellation": "SingleQubitGateCancellation",
    "bell_state_preparation": "BellStatePreparation",
    "swap_from_three_cx": "SwapFromThreeCx",
}

KERNEL_THEOREM_CONTENT: dict[str, str] = {
    "cnot_self_inverse_cancellation": (
        "theorem bridge_cnot_codegen_self_inverse (i j : Fin 4) : "
        "denotateOps2 QSpecBench.Generated.CnotSelfInverse.ops i j = id4 i j"
    ),
    "hadamard_conjugates_x_to_z": (
        "theorem bridge_hadamard_codegen_conjugates_x (i j : Fin 2) : "
        "denotateOps1IntScaffold QSpecBench.Generated.HadamardConjugatesXToZ.ops i j = scale2 2 pauliZ2 i j"
    ),
    "single_qubit_gate_cancellation": (
        "theorem bridge_hadamard_codegen_cancel (i j : Fin 2) : "
        "denotateOps1IntScaffold QSpecBench.Generated.SingleQubitGateCancellation.ops i j = scale2 2 id2 i j"
    ),
    "bell_state_preparation": (
        "theorem bridge_bell_codegen_prep (i j : Fin 4) : "
        "denotateOps2 QSpecBench.Generated.BellStatePreparation.ops i j = bellPrepMatrix i j"
    ),
    "swap_from_three_cx": (
        "theorem bridge_swap_from_three_cx_codegen (i j : Fin 4) : "
        "denotateOps2 QSpecBench.Generated.SwapFromThreeCx.ops i j = swap4 i j"
    ),
}


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


def theorem_content_sha256(benchmark_id: str) -> str | None:
    content = KERNEL_THEOREM_CONTENT.get(benchmark_id)
    if not content:
        return None
    payload = json.dumps(
        {"theorem_content": content, "kind": KERNEL_CHECKED_LINK},
        sort_keys=True,
        separators=(",", ":"),
    )
    return _sha256_bytes(payload.encode("utf-8"))


KERNEL_CHECKED_THEOREMS: dict[str, str] = {
    "cnot_self_inverse_cancellation": "QSpecBench.Quantum.OpenQASM3.bridge_cnot_codegen_self_inverse",
    "hadamard_conjugates_x_to_z": "QSpecBench.Quantum.OpenQASM3.bridge_hadamard_codegen_conjugates_x",
    "single_qubit_gate_cancellation": "QSpecBench.Quantum.OpenQASM3.bridge_hadamard_codegen_cancel",
    "bell_state_preparation": "QSpecBench.Quantum.OpenQASM3.bridge_bell_codegen_prep",
    "swap_from_three_cx": "QSpecBench.Quantum.OpenQASM3.bridge_swap_from_three_cx_codegen",
}


def kernel_checked_theorem_name(benchmark_id: str) -> str | None:
    return KERNEL_CHECKED_THEOREMS.get(benchmark_id)


def codegen_output_path(claim_dir: Path, benchmark_id: str) -> Path:
    safe_id = re.sub(r"[^a-zA-Z0-9_]", "_", benchmark_id)
    return claim_dir / "evidence" / f"{safe_id}_codegen_ops.lean"


def generate_for_benchmark(claim_dir: Path, *, qasm_role: str = "source") -> dict[str, Any]:
    """Generate Lean stub + hashes for one benchmark (source or target QASM)."""
    import yaml

    spec_path = claim_dir / "spec.yaml"
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    benchmark_id = spec.get("id", claim_dir.name)
    extraction = spec.get("qasm_extraction")

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

    qasm_path = claim_dir / qasm_rel
    ast = build_canonical_ast(qasm_path, extraction=extraction)
    stub_id = benchmark_id if qasm_role == "source" else f"{benchmark_id}_target"
    lean_text = generate_lean_stub(stub_id, ast, witness=True)
    out_path = codegen_output_path(claim_dir, stub_id)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(lean_text, encoding="utf-8")

    package_path = package_lean_path(stub_id)
    package_rel: str | None = None
    if package_path is not None:
        package_path.parent.mkdir(parents=True, exist_ok=True)
        package_text = generate_lean_stub(stub_id, ast, witness=False)
        package_path.write_text(package_text, encoding="utf-8")
        package_rel = str(package_path.relative_to(REPO_ROOT))

    artifact_sha, trace_sha, _trace = compute_bridge_hashes(qasm_path, extraction=extraction)
    return {
        "benchmark_id": benchmark_id,
        "qasm_role": qasm_role,
        "qasm_artifact": qasm_rel,
        "artifact_sha256": artifact_sha,
        "gate_trace_sha256": trace_sha,
        "ast": ast,
        "ast_sha256": ast_sha256(ast),
        "generated_lean_path": str(out_path.relative_to(claim_dir)),
        "generated_lean_sha256": generated_lean_sha256(lean_text),
        "package_lean_path": package_rel,
        "package_lean_sha256": generated_lean_sha256(package_text) if package_path else None,
    }


def verify_manifest_target_codegen(entry: dict[str, Any], claim_dir: Path) -> list[str]:
    """Verify target-side ast_sha256 and generated_lean_sha256 when present."""
    errors: list[str] = []
    benchmark_id = entry.get("benchmark_id", "")
    if not entry.get("target_ast_sha256") and not entry.get("target_generated_lean_sha256"):
        return errors
    try:
        result = generate_for_benchmark(claim_dir, qasm_role="target")
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
        result = generate_for_benchmark(claim_dir)
    except (FileNotFoundError, ValueError) as exc:
        return [f"codegen verify failed for {benchmark_id}: {exc}"]

    if entry.get("ast_sha256") and entry["ast_sha256"] != result["ast_sha256"]:
        errors.append(
            f"ast_sha256 drift for {benchmark_id}: manifest != regenerated canonical AST"
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
            content_hash = theorem_content_sha256(benchmark_id)
            if content_hash:
                entry["theorem_content_sha256"] = content_hash
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
    expected_content = theorem_content_sha256(benchmark_id)
    if expected_content and entry.get("theorem_content_sha256"):
        if entry["theorem_content_sha256"] != expected_content:
            errors.append(f"theorem_content_sha256 drift for {benchmark_id}")
    if not entry.get("ast_sha256") or not entry.get("generated_lean_sha256"):
        errors.append(
            f"{KERNEL_CHECKED_LINK} requires ast_sha256 and generated_lean_sha256 for {benchmark_id}"
        )
    if not stored_id:
        errors.append(f"{KERNEL_CHECKED_LINK} requires theorem_identifier_sha256 for {benchmark_id}")
    if expected_content and not entry.get("theorem_content_sha256"):
        errors.append(f"{KERNEL_CHECKED_LINK} requires theorem_content_sha256 for {benchmark_id}")
    if not generated_module_name(benchmark_id):
        errors.append(f"kernel bridge {benchmark_id} missing generated module mapping")
    return errors

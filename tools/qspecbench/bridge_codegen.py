"""OpenQASM → canonical AST → Lean stub generator (pilot).

See docs/bridge_codegen_design.md. This module wires ast_sha256 and
generated_lean_sha256 into bridge_theorem_manifest.json; it does not by itself
establish kernel_checked_artifact_semantics (no kernel proof that generated ops
denote the QASM artifact matrix).
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

CANONICAL_AST_VERSION = "0.1"

_SINGLE_GATES = {"i", "x", "y", "z", "h", "s", "t", "sdg", "tdg"}


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


def generate_lean_stub(
    benchmark_id: str,
    ast: dict[str, Any],
    *,
    module: str = "QSpecBench.Quantum.OpenQASM3",
) -> str:
    """Emit a Lean snippet declaring a QasmOp list from canonical AST."""
    safe_id = re.sub(r"[^a-zA-Z0-9_]", "_", benchmark_id)
    ops_name = f"{safe_id}_codegen_ops"
    items = ", ".join(_lean_op_item(g) for g in ast["gates"])
    return (
        "/- QSpecBench bridge codegen (pilot): regenerate via "
        "`qspecbench bridge-codegen generate`. -/\n"
        f"import {module}\n\n"
        f"open {module}\n\n"
        f"def {ops_name} : List QasmOp := [{items}]\n"
    )


def generated_lean_sha256(text: str) -> str:
    normalized = text.replace("\r\n", "\n").encode("utf-8")
    return _sha256_bytes(normalized)


def codegen_output_path(claim_dir: Path, benchmark_id: str) -> Path:
    safe_id = re.sub(r"[^a-zA-Z0-9_]", "_", benchmark_id)
    return claim_dir / "evidence" / f"{safe_id}_codegen_ops.lean"


def generate_for_benchmark(claim_dir: Path) -> dict[str, Any]:
    """Generate Lean stub + hashes for one benchmark."""
    import yaml

    spec_path = claim_dir / "spec.yaml"
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    benchmark_id = spec.get("id", claim_dir.name)
    extraction = spec.get("qasm_extraction")

    bridge_path = claim_dir / "expected" / "semantic_bridge.json"
    qasm_rel: str | None = None
    if bridge_path.is_file():
        bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
        qasm_rel = bridge.get("qasm_artifact")
    if not qasm_rel:
        for obj in spec.get("objects", []):
            if obj.get("format") == "qasm3" and obj.get("role") == "source":
                qasm_rel = obj.get("path")
                break
    if not qasm_rel:
        raise FileNotFoundError(f"no qasm3 source artifact for {benchmark_id}")

    qasm_path = claim_dir / qasm_rel
    ast = build_canonical_ast(qasm_path, extraction=extraction)
    lean_text = generate_lean_stub(benchmark_id, ast)
    out_path = codegen_output_path(claim_dir, benchmark_id)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(lean_text, encoding="utf-8")

    artifact_sha, trace_sha, _trace = compute_bridge_hashes(qasm_path, extraction=extraction)
    return {
        "benchmark_id": benchmark_id,
        "qasm_artifact": qasm_rel,
        "artifact_sha256": artifact_sha,
        "gate_trace_sha256": trace_sha,
        "ast": ast,
        "ast_sha256": ast_sha256(ast),
        "generated_lean_path": str(out_path.relative_to(claim_dir)),
        "generated_lean_sha256": generated_lean_sha256(lean_text),
    }


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
    return errors


def update_manifest_entry(benchmark_id: str, result: dict[str, Any]) -> None:
    """Write ast_sha256 and generated_lean_sha256 into bridge_theorem_manifest.json."""
    manifest = load_manifest()
    updated = False
    for entry in manifest.get("entries", []):
        if entry.get("benchmark_id") != benchmark_id:
            continue
        entry["ast_sha256"] = result["ast_sha256"]
        entry["generated_lean_sha256"] = result["generated_lean_sha256"]
        entry["obligation_ids"] = entry.get("obligation_ids") or ["semantic_bridge"]
        updated = True
        break
    if not updated:
        raise KeyError(f"benchmark_id {benchmark_id!r} not in {MANIFEST_PATH}")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

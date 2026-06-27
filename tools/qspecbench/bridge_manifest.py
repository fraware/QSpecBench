"""Kernel bridge manifest: tie QASM artifacts to Lean theorems by hash and gate trace."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from qspecbench.denotate import ops_from_qasm_matrix
from qspecbench.qasm_matrix import extract_matrix
from qspecbench.schema import REPO_ROOT

MANIFEST_PATH = REPO_ROOT / "schema" / "bridge_theorem_manifest.json"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _gate_trace(ops: list[Any]) -> list[list[Any]]:
    trace: list[list[Any]] = []
    for op in ops:
        gate, args, angle = op[0], op[1], op[2] if len(op) > 2 else None
        g = gate.lower()
        if g == "rx" and angle is not None:
            trace.append(["rx", list(args), angle])
        elif g == "ry" and angle is not None:
            trace.append(["ry", list(args), angle])
        elif g == "rz" and angle is not None:
            trace.append(["rz", list(args), angle])
        elif g == "u" and len(args) >= 4:
            trace.append(["u", [args[0]], args[1], args[2], args[3]])
        elif g in {"cx", "cnot"}:
            trace.append(["cx", list(args)])
        elif g == "cz":
            trace.append(["cz", list(args)])
        elif g == "ccx":
            trace.append(["ccx", list(args)])
        elif g == "swap":
            trace.append(["swap", list(args)])
        else:
            trace.append([g, list(args)])
    return trace


def _gate_trace_sha256(trace: list[list[Any]]) -> str:
    payload = json.dumps(trace, sort_keys=True, separators=(",", ":"))
    return _sha256_bytes(payload.encode("utf-8"))


def load_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.is_file():
        return {"entries": []}
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def manifest_entry_for_theorem(theorem: str) -> dict[str, Any] | None:
    for entry in load_manifest().get("entries", []):
        if entry.get("lean_theorem") == theorem:
            return entry
    return None


def compute_bridge_hashes(qasm_path: Path) -> tuple[str, str, list[list[Any]]]:
    qasm_data = extract_matrix(qasm_path)
    ops = ops_from_qasm_matrix(qasm_data)
    trace = _gate_trace(ops)
    return _sha256_file(qasm_path), _gate_trace_sha256(trace), trace


def _find_qasm_for_bridge(claim_dir: Path, bridge: dict[str, Any]) -> Path | None:
    rel = bridge.get("qasm_artifact")
    if rel:
        candidate = claim_dir / rel
        if candidate.is_file():
            return candidate
    for obj in _load_spec(claim_dir).get("objects", []):
        if obj.get("format") == "qasm3" and obj.get("role") == "source" and obj.get("path"):
            candidate = claim_dir / obj["path"]
            if candidate.is_file():
                return candidate
    return None


def _load_spec(claim_dir: Path) -> dict[str, Any]:
    import yaml

    return yaml.safe_load((claim_dir / "spec.yaml").read_text(encoding="utf-8"))


def _lean_evidence_references_theorem(claim_dir: Path, spec: dict[str, Any], theorem: str) -> bool:
    for ev in spec.get("evidence", []):
        if ev.get("type") != "lean_proof" or ev.get("status") != "passing":
            continue
        path = claim_dir / ev.get("path", "")
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if theorem in text or f"#check {theorem}" in text:
            return True
        module = theorem.split(".")[0] if "." in theorem else theorem
        if module in text:
            return True
    return False


def validate_kernel_bridge(claim_dir: Path, bridge: dict[str, Any], spec: dict[str, Any]) -> list[str]:
    """Validate kernel_checked bridge requirements."""
    errors: list[str] = []
    theorem = bridge.get("lean_theorem", "")
    if not theorem:
        errors.append("kernel_checked bridge requires lean_theorem")
        return errors

    entry = manifest_entry_for_theorem(theorem)
    if entry is None:
        errors.append(f"lean_theorem {theorem!r} not in bridge_theorem_manifest.json allowlist")
        return errors

    if entry.get("benchmark_id") and entry["benchmark_id"] != spec.get("id"):
        errors.append(
            f"manifest benchmark_id {entry['benchmark_id']!r} != spec id {spec.get('id')!r}"
        )

    qasm = _find_qasm_for_bridge(claim_dir, bridge)
    if qasm is None:
        errors.append("kernel_checked bridge requires a qasm3 artifact")
        return errors

    artifact_sha, trace_sha, trace = compute_bridge_hashes(qasm)
    if bridge.get("artifact_sha256") and bridge["artifact_sha256"] != artifact_sha:
        errors.append("semantic_bridge artifact_sha256 drift: QASM artifact changed")
    if bridge.get("gate_trace_sha256") and bridge["gate_trace_sha256"] != trace_sha:
        errors.append("semantic_bridge gate_trace_sha256 drift: extracted gate trace changed")
    if entry.get("artifact_sha256") and entry["artifact_sha256"] != artifact_sha:
        errors.append("artifact_sha256 drift: QASM artifact changed since manifest was recorded")
    if entry.get("gate_trace_sha256") and entry["gate_trace_sha256"] != trace_sha:
        errors.append("gate_trace_sha256 drift: extracted gate trace changed since manifest was recorded")
    if entry.get("gate_trace") and entry["gate_trace"] != trace:
        errors.append("gate_trace mismatch against bridge_theorem_manifest.json")

    if not _lean_evidence_references_theorem(claim_dir, spec, theorem):
        errors.append(
            f"passing lean_proof evidence must reference theorem {theorem!r} (import or #check)"
        )

    formal = spec.get("formal_claims") or []
    if not any(fc.get("theorem", "").endswith(theorem.split(".")[-1]) or fc.get("theorem") == theorem for fc in formal):
        errors.append(f"formal_claims must declare theorem binding for {theorem!r}")

    return errors

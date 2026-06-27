"""Bridge manifest: tie QASM artifacts to Lean theorems by hash and gate trace."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from qspecbench.denotate import ops_from_qasm_matrix
from qspecbench.qasm_matrix import extract_matrix
from qspecbench.schema import REPO_ROOT

MANIFEST_PATH = REPO_ROOT / "schema" / "bridge_theorem_manifest.json"

# Structured Lean evidence anchor (exact fields, exact #check line).
EVIDENCE_ANCHOR_RE = re.compile(
    r"/-\s*QSpecBench evidence:\s*"
    r"benchmark_id\s*=\s*\"(?P<benchmark_id>[^\"]+)\"\s*"
    r"obligation_id\s*=\s*\"(?P<obligation_id>[^\"]+)\"\s*"
    r"theorem\s*=\s*\"(?P<theorem>[^\"]+)\"\s*"
    r"artifact_sha256\s*=\s*\"(?P<artifact_sha256>[a-f0-9]{64})\"\s*"
    r"gate_trace_sha256\s*=\s*\"(?P<gate_trace_sha256>[a-f0-9]{64})\"\s*"
    r"-/",
    re.DOTALL,
)


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


def full_theorem_name(bridge: dict[str, Any]) -> str:
    module = bridge.get("lean_module", "")
    theorem = bridge.get("lean_theorem", "")
    if module and theorem and not theorem.startswith(module):
        return f"{module}.{theorem}"
    return theorem


def compute_bridge_hashes(
    qasm_path: Path,
    extraction: dict[str, Any] | None = None,
) -> tuple[str, str, list[list[Any]]]:
    qasm_data = extract_matrix(qasm_path, extraction=extraction)
    ops = ops_from_qasm_matrix(qasm_data)
    trace = _gate_trace(ops)
    return _sha256_file(qasm_path), _gate_trace_sha256(trace), trace


def format_evidence_anchor(
    *,
    benchmark_id: str,
    obligation_id: str,
    theorem: str,
    artifact_sha256: str,
    gate_trace_sha256: str,
) -> str:
    return (
        "/- QSpecBench evidence:\n"
        f'benchmark_id = "{benchmark_id}"\n'
        f'obligation_id = "{obligation_id}"\n'
        f'theorem = "{theorem}"\n'
        f'artifact_sha256 = "{artifact_sha256}"\n'
        f'gate_trace_sha256 = "{gate_trace_sha256}"\n'
        "-/"
    )


def validate_lean_evidence_anchor(
    text: str,
    *,
    benchmark_id: str,
    theorem: str,
    artifact_sha256: str,
    gate_trace_sha256: str,
    obligation_id: str = "semantic_bridge",
) -> list[str]:
    """Validate structured comment block and exact #check line."""
    errors: list[str] = []
    match = EVIDENCE_ANCHOR_RE.search(text)
    if not match:
        errors.append(
            "passing lean_proof evidence must include structured QSpecBench evidence anchor block"
        )
        return errors

    fields = match.groupdict()
    if fields["benchmark_id"] != benchmark_id:
        errors.append(
            f"evidence anchor benchmark_id {fields['benchmark_id']!r} != {benchmark_id!r}"
        )
    if fields["obligation_id"] != obligation_id:
        errors.append(
            f"evidence anchor obligation_id {fields['obligation_id']!r} != {obligation_id!r}"
        )
    if fields["theorem"] != theorem:
        errors.append(f"evidence anchor theorem {fields['theorem']!r} != {theorem!r}")
    if fields["artifact_sha256"] != artifact_sha256:
        errors.append("evidence anchor artifact_sha256 does not match semantic_bridge manifest")
    if fields["gate_trace_sha256"] != gate_trace_sha256:
        errors.append("evidence anchor gate_trace_sha256 does not match semantic_bridge manifest")

    expected_check = f"#check {theorem}"
    lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("//")]
    if expected_check not in lines:
        errors.append(
            f"passing lean_proof evidence must contain exact line {expected_check!r} "
            "(not substring-only theorem reference)"
        )
    return errors


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


def _lean_evidence_for_bridge(
    claim_dir: Path,
    spec: dict[str, Any],
    bridge: dict[str, Any],
    theorem: str,
    artifact_sha256: str,
    gate_trace_sha256: str,
) -> list[str]:
    """Find passing lean_proof tied to bridge and validate strict anchor."""
    errors: list[str] = []
    benchmark_id = spec.get("id", "")
    bridge_evidence_id = bridge.get("bridge_evidence_id") or "bridge_verify"
    formal_theorem = bridge.get("lean_theorem", "")

    matched = False
    for ev in spec.get("evidence", []):
        if ev.get("type") != "lean_proof" or ev.get("status") != "passing":
            continue
        path = claim_dir / ev.get("path", "")
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        # Prefer evidence referenced by formal_claims for the bridge theorem.
        supports_bridge = any(
            fc.get("theorem") == formal_theorem or fc.get("theorem", "").endswith(f".{formal_theorem}")
            for fc in spec.get("formal_claims") or []
            if fc.get("evidence_id") == ev.get("id")
        )
        if not supports_bridge and formal_theorem not in text and f"#check {theorem}" not in text:
            continue
        matched = True
        errors.extend(
            validate_lean_evidence_anchor(
                text,
                benchmark_id=benchmark_id,
                theorem=theorem,
                artifact_sha256=artifact_sha256,
                gate_trace_sha256=gate_trace_sha256,
            )
        )
        break

    if not matched:
        errors.append(
            f"passing lean_proof evidence must reference theorem {theorem!r} with structured anchor"
        )
    return errors


def validate_manifest_bridge(claim_dir: Path, bridge: dict[str, Any], spec: dict[str, Any]) -> list[str]:
    """Validate manifest_checked_theorem_binding bridge requirements."""
    errors: list[str] = []
    theorem_short = bridge.get("lean_theorem", "")
    if not theorem_short:
        errors.append("manifest_checked_theorem_binding bridge requires lean_theorem")
        return errors

    entry = manifest_entry_for_theorem(theorem_short)
    if entry is None:
        errors.append(
            f"lean_theorem {theorem_short!r} not in bridge_theorem_manifest.json allowlist"
        )
        return errors

    if entry.get("benchmark_id") and entry["benchmark_id"] != spec.get("id"):
        errors.append(
            f"manifest benchmark_id {entry['benchmark_id']!r} != spec id {spec.get('id')!r}"
        )

    qasm = _find_qasm_for_bridge(claim_dir, bridge)
    if qasm is None:
        errors.append("manifest_checked_theorem_binding bridge requires a qasm3 artifact")
        return errors

    extraction = spec.get("qasm_extraction")
    artifact_sha, trace_sha, trace = compute_bridge_hashes(qasm, extraction=extraction)
    theorem_full = full_theorem_name(bridge)

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

    errors.extend(
        _lean_evidence_for_bridge(
            claim_dir,
            spec,
            bridge,
            theorem_full,
            artifact_sha,
            trace_sha,
        )
    )

    formal = spec.get("formal_claims") or []
    if not any(
        fc.get("theorem", "").endswith(theorem_short.split(".")[-1])
        or fc.get("theorem") == theorem_short
        or fc.get("theorem") == theorem_full
        for fc in formal
    ):
        errors.append(f"formal_claims must declare theorem binding for {theorem_short!r}")

    return errors


# Backward-compatible alias during migration tooling.
validate_kernel_bridge = validate_manifest_bridge

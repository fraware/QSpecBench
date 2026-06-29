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

    if entry.get("target_qasm_artifact"):
        target_path = claim_dir / entry["target_qasm_artifact"]
        if not target_path.is_file():
            errors.append(f"target qasm artifact missing: {entry['target_qasm_artifact']}")
        else:
            targ_sha, targ_trace_sha, targ_trace = compute_bridge_hashes(
                target_path, extraction=extraction
            )
            if entry.get("target_artifact_sha256") and entry["target_artifact_sha256"] != targ_sha:
                errors.append("target_artifact_sha256 drift: target QASM artifact changed")
            if entry.get("target_gate_trace_sha256") and entry["target_gate_trace_sha256"] != targ_trace_sha:
                errors.append("target_gate_trace_sha256 drift: target gate trace changed")
            if entry.get("target_gate_trace") and entry["target_gate_trace"] != targ_trace:
                errors.append("target_gate_trace mismatch against bridge_theorem_manifest.json")

    if entry.get("ast_sha256") or entry.get("generated_lean_sha256"):
        from qspecbench.bridge_codegen import verify_manifest_codegen

        errors.extend(verify_manifest_codegen(entry, claim_dir))

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


def validate_kernel_checked_bridge(claim_dir: Path, bridge: dict[str, Any], spec: dict[str, Any]) -> list[str]:
    """Validate kernel_checked_codegen_trace bridge (codegen + kernel proof chain)."""
    from qspecbench.bridge_codegen import (
        GENERATED_MODULE_MAP,
        KERNEL_CHECKED_LINK,
        LEGACY_KERNEL_CHECKED_LINK,
        kernel_checked_theorem_name,
        read_theorem_source_hash,
        theorem_source_statement_hash,
        verify_kernel_checked_entry,
    )

    errors = validate_manifest_bridge(claim_dir, bridge, spec)
    theorem_short = bridge.get("lean_theorem", "")
    entry = manifest_entry_for_theorem(theorem_short)
    if entry is None:
        return errors

    benchmark_id = spec.get("id", "")
    expected = kernel_checked_theorem_name(benchmark_id)
    if expected is None:
        errors.append(f"benchmark {benchmark_id!r} has no kernel_checked theorem mapping")
        return errors

    expected_short = expected.split(".")[-1]
    if theorem_short != expected_short:
        errors.append(
            f"kernel_checked bridge lean_theorem must be {expected_short!r}, got {theorem_short!r}"
        )

    errors.extend(verify_kernel_checked_entry(entry, claim_dir))

    if bridge.get("ast_sha256") and entry.get("ast_sha256") and bridge["ast_sha256"] != entry["ast_sha256"]:
        errors.append("semantic_bridge ast_sha256 does not match manifest codegen ast_sha256")
    if (
        bridge.get("generated_lean_sha256")
        and entry.get("generated_lean_sha256")
        and bridge["generated_lean_sha256"] != entry["generated_lean_sha256"]
    ):
        errors.append(
            "semantic_bridge generated_lean_sha256 does not match manifest codegen hash"
        )
    id_hash = bridge.get("theorem_identifier_sha256") or bridge.get("theorem_sha256")
    entry_id = entry.get("theorem_identifier_sha256") or entry.get("theorem_sha256")
    if id_hash and entry_id and id_hash != entry_id:
        errors.append("semantic_bridge theorem_identifier_sha256 does not match manifest")
    content_hash = theorem_source_statement_hash(benchmark_id)
    bridge_hash = read_theorem_source_hash(bridge)
    if content_hash and bridge_hash:
        if bridge_hash != content_hash:
            errors.append("semantic_bridge theorem_source_statement_hash does not match manifest")
    elif content_hash and not bridge_hash:
        errors.append("semantic_bridge missing theorem_source_statement_hash for kernel-checked bridge")

    claimed = bridge.get("claimed_link")
    module_name = GENERATED_MODULE_MAP.get(benchmark_id)
    if claimed == LEGACY_KERNEL_CHECKED_LINK:
        if not module_name:
            errors.append(
                f"{LEGACY_KERNEL_CHECKED_LINK} requires generated module for {benchmark_id!r}"
            )
        else:
            openqasm3 = REPO_ROOT / "lean" / "QSpecBench" / "Quantum" / "OpenQASM3.lean"
            if openqasm3.is_file():
                text = openqasm3.read_text(encoding="utf-8")
                import_line = f"import QSpecBench.Generated.{module_name}"
                use_generated = f"Generated.{module_name}.ops"
                if import_line not in text or use_generated not in text:
                    errors.append(
                        f"{LEGACY_KERNEL_CHECKED_LINK} requires OpenQASM3 theorem to import "
                        f"and use QSpecBench.Generated.{module_name}.ops"
                    )
    if claimed == KERNEL_CHECKED_LINK and module_name is None:
        errors.append(f"{KERNEL_CHECKED_LINK} benchmark {benchmark_id!r} missing generated module map")

    return errors


# Backward-compatible alias during migration tooling.
validate_kernel_bridge = validate_manifest_bridge

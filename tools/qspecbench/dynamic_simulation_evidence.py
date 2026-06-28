"""Stale detection for dynamic simulation evidence JSON."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from qspecbench.validate import load_spec


def _sha256_payload(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def dynamic_simulation_fingerprint(report: dict[str, Any]) -> str:
    """Stable hash of a simulation report (excludes embedded fingerprint field)."""
    payload = {k: v for k, v in report.items() if k != "report_fingerprint"}
    return _sha256_payload(payload)


def regenerate_dynamic_simulation_report(claim_dir: Path, spec: dict[str, Any]) -> dict[str, Any] | None:
    """Regenerate the expected simulation report for a claim, if applicable."""
    from qspecbench.dynamic_simulator import verify_teleportation_basis_states

    bid = spec.get("id", claim_dir.name)
    if bid == "teleportation_preserves_state_up_to_pauli_correction":
        qasm = None
        for obj in spec.get("objects", []):
            if obj.get("format") == "qasm3" and obj.get("path"):
                qasm = claim_dir / obj["path"]
                break
        if qasm is None or not qasm.is_file():
            return None
        return verify_teleportation_basis_states(qasm, spec.get("qasm_extraction"))
    return None


def attach_fingerprint(report: dict[str, Any]) -> dict[str, Any]:
    out = dict(report)
    out["report_fingerprint"] = dynamic_simulation_fingerprint(report)
    return out


def validate_dynamic_simulation_evidence(claim_dir: Path, spec: dict[str, Any] | None = None) -> list[str]:
    """Fail if simulation evidence JSON is stale vs regenerated report."""
    if spec is None:
        spec_path = claim_dir / "spec.yaml"
        if not spec_path.is_file():
            return []
        spec = load_spec(spec_path)

    errors: list[str] = []
    for ev in spec.get("evidence", []):
        if ev.get("type") != "simulation":
            continue
        path = ev.get("path")
        if not path or not str(path).endswith(".json"):
            continue
        evidence_path = claim_dir / path
        if not evidence_path.is_file():
            continue
        try:
            stored = json.loads(evidence_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            errors.append(f"{path}: invalid JSON")
            continue
        regenerated = regenerate_dynamic_simulation_report(claim_dir, spec)
        if regenerated is None:
            continue
        expected = attach_fingerprint(regenerated)
        stored_fp = stored.get("report_fingerprint")
        expected_fp = expected["report_fingerprint"]
        if stored_fp == expected_fp:
            continue
        if stored == {k: v for k, v in expected.items() if k != "report_fingerprint"}:
            errors.append(
                f"{path} stale vs regenerated dynamic simulation "
                f"(fingerprint {expected_fp[:12]}…; regenerate via dynamic-simulate CLI)"
            )
        elif stored_fp and stored_fp != expected_fp:
            errors.append(
                f"{path} report_fingerprint stale "
                f"(expected {expected_fp[:12]}…, got {stored_fp[:12]}…)"
            )
        else:
            errors.append(
                f"{path} stale vs regenerated dynamic simulation "
                "(regenerate via `qspecbench dynamic-simulate --teleport-basis-check`)"
            )
    return errors

"""Stale detection for dynamic simulation evidence JSON."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from qspecbench.schema import REPO_ROOT
from qspecbench.validate import load_spec

MEASUREMENT_LEAN = REPO_ROOT / "lean" / "QSpecBench" / "Quantum" / "Measurement.lean"
_THEOREM_NAME_RE = re.compile(r"\b(?:theorem|lemma|def)\s+([A-Za-z0-9_']+)")


def _sha256_payload(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def dynamic_simulation_fingerprint(report: dict[str, Any]) -> str:
    """Stable hash of a simulation report (excludes embedded fingerprint fields)."""
    payload = {
        k: v
        for k, v in report.items()
        if k not in ("report_fingerprint", "input_fingerprint")
    }
    return _sha256_payload(payload)


def dynamic_simulation_input_fingerprint(claim_dir: Path, spec: dict[str, Any]) -> str | None:
    """Hash of simulation inputs (QASM bytes + extraction config + benchmark id)."""
    qasm_path = None
    for obj in spec.get("objects", []):
        if obj.get("format") == "qasm3" and obj.get("path"):
            qasm_path = claim_dir / obj["path"]
            break
    if qasm_path is None or not qasm_path.is_file():
        return None
    payload = {
        "benchmark_id": spec.get("id", claim_dir.name),
        "qasm_sha256": hashlib.sha256(qasm_path.read_bytes()).hexdigest(),
        "qasm_extraction": spec.get("qasm_extraction") or {},
    }
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
        return attach_lean_cross_refs(
            verify_teleportation_basis_states(qasm, spec.get("qasm_extraction")),
            spec,
        )
    return None


_LEAN_MEASUREMENT_THEOREM_REFS = (
    "QSpecBench.Quantum.Measurement.measure_state00_q0_zero",
    "QSpecBench.Quantum.Measurement.postMeasure_state00_unchanged_at_basis",
    "QSpecBench.Quantum.Measurement.pauli_x4_corrects_state01_at_receiver",
    "QSpecBench.Quantum.Measurement.pauli_z4_flips_sign_on_state11_at_basis",
    "QSpecBench.Quantum.Measurement.pauli_x8_corrects_state001_at_receiver",
    "QSpecBench.Quantum.Measurement.pauli_z8_flips_sign_on_state101_at_basis",
    "QSpecBench.Quantum.Measurement.teleport_basis001_lemma_chain",
    "QSpecBench.Quantum.Measurement.teleport_pauli_correction_anchor_note",
)


def _theorem_short_name(ref: str) -> str:
    return ref.rsplit(".", 1)[-1]


def _lean_symbol_names(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    return set(_THEOREM_NAME_RE.findall(path.read_text(encoding="utf-8")))


def _measurement_evidence_lean_paths(claim_dir: Path, spec: dict[str, Any]) -> list[Path]:
    paths: list[Path] = []
    for ev in spec.get("evidence", []):
        if ev.get("type") != "lean_proof":
            continue
        rel = ev.get("path")
        if rel and str(rel).endswith(".lean"):
            paths.append(claim_dir / rel)
    return paths


def validate_lean_theorem_refs(
    refs: list[str],
    *,
    claim_dir: Path | None = None,
    spec: dict[str, Any] | None = None,
) -> list[str]:
    """Fail closed when cross-ref names are absent from Measurement.lean or evidence Lean files."""
    errors: list[str] = []
    allowed = _lean_symbol_names(MEASUREMENT_LEAN)
    if claim_dir is not None and spec is not None:
        for path in _measurement_evidence_lean_paths(claim_dir, spec):
            allowed |= _lean_symbol_names(path)
    if not allowed:
        errors.append("lean cross-ref validation failed: Measurement.lean symbols unavailable")
        return errors
    for ref in refs:
        short = _theorem_short_name(ref)
        if short not in allowed:
            errors.append(
                f"lean_cross_ref.lean_theorem_refs missing symbol {ref!r} "
                f"(expected theorem/def in Measurement.lean or evidence lean files)"
            )
    return errors


def lean_measurement_cross_refs() -> dict[str, Any]:
    """Lean theorem names anchoring basis-state measurement / Pauli correction checks."""
    return {
        "lean_theorem_refs": list(_LEAN_MEASUREMENT_THEOREM_REFS),
        "trust_boundary": (
            "Basis-state scaffold only; arbitrary superposition update not kernel-checked."
        ),
    }


def attach_lean_cross_refs(report: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    bid = spec.get("id", "")
    if bid == "teleportation_preserves_state_up_to_pauli_correction":
        out = dict(report)
        out["lean_cross_ref"] = lean_measurement_cross_refs()
        return out
    return report


def attach_fingerprint(
    report: dict[str, Any],
    *,
    input_fingerprint: str | None = None,
) -> dict[str, Any]:
    out = dict(report)
    if input_fingerprint is not None:
        out["input_fingerprint"] = input_fingerprint
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

        current_input_fp = dynamic_simulation_input_fingerprint(claim_dir, spec)
        stored_fp = stored.get("report_fingerprint")
        stored_input_fp = stored.get("input_fingerprint")
        if (
            current_input_fp
            and stored_input_fp == current_input_fp
            and stored_fp
            and stored_fp == dynamic_simulation_fingerprint(stored)
        ):
            cross_errors = validate_lean_theorem_refs(
                stored.get("lean_cross_ref", {}).get("lean_theorem_refs") or [],
                claim_dir=claim_dir,
                spec=spec,
            )
            errors.extend(f"{path}: {e}" for e in cross_errors)
            continue

        regenerated = regenerate_dynamic_simulation_report(claim_dir, spec)
        if regenerated is None:
            continue
        expected = attach_fingerprint(
            regenerated,
            input_fingerprint=current_input_fp,
        )
        stored_fp = stored.get("report_fingerprint")
        expected_fp = expected["report_fingerprint"]
        if stored_fp == expected_fp:
            cross_errors = validate_lean_theorem_refs(
                stored.get("lean_cross_ref", {}).get("lean_theorem_refs") or [],
                claim_dir=claim_dir,
                spec=spec,
            )
            errors.extend(f"{path}: {e}" for e in cross_errors)
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

"""Evidence path and adapter-binding validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qspecbench.adapter_registry import validate_evidence_adapter_binding
from qspecbench.artifacts import claim_path_escape_error, resolve_claim_path
from qspecbench.evidence_adapter_bindings import validate_evidence_adapter_bindings_sidecar
from qspecbench.models import REFERENCE_CLAIM_LEVEL


REQUIRED_ARTIFACT_BOUND_REVIEWS = ("formal_evidence_review", "domain_semantics_review")


def validate_evidence_paths(spec: dict[str, Any], claim_dir: Path) -> list[str]:
    errors: list[str] = []
    for ev in spec.get("evidence", []):
        path = ev.get("path")
        if not path:
            continue
        escape_err = claim_path_escape_error(claim_dir, path)
        if escape_err:
            errors.append(escape_err)
        elif not resolve_claim_path(claim_dir, path).is_file():
            errors.append(f"missing evidence file: {path}")
    return errors


def validate_evidence_rules(spec: dict[str, Any], claim_dir: Path) -> list[str]:
    from qspecbench.dynamic_simulation_evidence import validate_dynamic_simulation_evidence

    errors: list[str] = []
    errors.extend(validate_evidence_adapter_binding(spec))
    errors.extend(validate_evidence_adapter_bindings_sidecar(spec, claim_dir))
    errors.extend(validate_evidence_paths(spec, claim_dir))
    errors.extend(validate_dynamic_simulation_evidence(claim_dir, spec))
    errors.extend(validate_qasm_extraction(spec))
    errors.extend(validate_ai_formalization_reviewer(spec))
    errors.extend(validate_permanent_residual_evidence_payloads(spec, claim_dir))
    return errors


def validate_permanent_residual_evidence_payloads(
    spec: dict[str, Any], claim_dir: Path
) -> list[str]:
    """Fail-closed honesty on ISA / Stim declared-universe evidence JSON."""
    import json

    from qspecbench.permanent_residuals import (
        validate_hardware_isa_payload,
        validate_stim_declared_universe_payload,
    )

    errors: list[str] = []
    for ev in spec.get("evidence", []):
        path = ev.get("path")
        if not path:
            continue
        full = resolve_claim_path(claim_dir, path)
        if not full.is_file() or not str(path).endswith(".json"):
            continue
        try:
            payload = json.loads(full.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(payload, dict):
            continue
        schema = str(payload.get("schema") or "")
        if schema == "qspecbench.hardware_isa_abstraction.v1":
            for msg in validate_hardware_isa_payload(payload):
                errors.append(f"evidence {ev.get('id')}: {msg}")
        elif schema in (
            "qspecbench.stim_declared_repetition_universe.v1",
            "qspecbench.stim_declared_surface_universe.v1",
        ):
            for msg in validate_stim_declared_universe_payload(payload):
                errors.append(f"evidence {ev.get('id')}: {msg}")
    return errors


def validate_ai_formalization_reviewer(spec: dict[str, Any]) -> list[str]:
    """Hard-fail ai_formalization reference_claim without named reviewer identity."""
    errors: list[str] = []
    if spec.get("track") != "ai_formalization":
        return errors
    maturity = spec.get("status", {}).get("maturity")
    if maturity != REFERENCE_CLAIM_LEVEL:
        return errors
    reviews = (spec.get("status") or {}).get("reviews") or {}
    for review_key in REQUIRED_ARTIFACT_BOUND_REVIEWS:
        block = reviews.get(review_key) or {}
        reviewer = (block.get("reviewer") or "").strip()
        if not reviewer:
            errors.append(
                f"ai_formalization {REFERENCE_CLAIM_LEVEL} requires "
                f"status.reviews.{review_key}.reviewer (named identity)"
            )
        elif reviewer == "maintainer-bootstrap":
            errors.append(
                f"ai_formalization {REFERENCE_CLAIM_LEVEL} requires "
                f"status.reviews.{review_key}.reviewer to be non-bootstrap"
            )
    return errors


def validate_qasm_extraction(spec: dict[str, Any]) -> list[str]:
    """Fail closed on unimplemented extraction modes."""
    extraction = spec.get("qasm_extraction")
    if not extraction:
        return []
    mode = extraction.get("mode")
    effective_mode = "dynamic_fragment_recording" if mode == "full_dynamic_semantics" else mode
    if effective_mode == "dynamic_fragment_recording":
        semantics_base = spec.get("semantics_base")
        if semantics_base != "dynamic_circuit":
            return [
                "qasm_extraction.mode=dynamic_fragment_recording requires "
                "semantics_base=dynamic_circuit (projective measurement stub + "
                "declared non-unitary skips)"
            ]
        allowed = set(extraction.get("allowed_to_skip") or [])
        if "measurement" not in allowed:
            return [
                "dynamic_fragment_recording requires allowed_to_skip to include "
                "'measurement' (projective POVM stub; unitary fragment insufficient)"
            ]
    return []


def validate_dynamic_circuit_qubit_limit(claim_dir: Path, spec: dict[str, Any]) -> list[str]:
    """Warn (non-fatal) when dynamic-circuit QASM artifacts exceed operational simulator limit."""
    if spec.get("semantics_base") != "dynamic_circuit":
        return []
    from qspecbench.dynamic_simulator import warn_operational_qubit_limit

    warnings: list[str] = []
    for obj in spec.get("objects", []):
        if obj.get("format") != "qasm3":
            continue
        path = obj.get("path")
        if not path:
            continue
        qasm = claim_dir / path
        warnings.extend(warn_operational_qubit_limit(qasm))
    return warnings

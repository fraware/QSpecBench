"""QEC witness and claim-scope validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

def _infer_qec_witness_claim_kind(spec: dict[str, Any]) -> str | None:
    """Map qec_claim_scope fields to witness claim_kind for semantic validation."""
    claim_id = spec.get("id", "")
    obligations = set(spec.get("proved_scope", {}).get("checked_obligations") or [])
    obligations.update(spec.get("claim_scope", {}).get("required_obligations") or [])
    scope = spec.get("qec_claim_scope") or {}

    if "syndrome_extraction" in claim_id or "syndrome_extraction" in obligations:
        return "syndrome_extraction"
    if scope.get("distance", {}).get("status") in {"checked", "complete"}:
        return "minimum_distance"
    if scope.get("syndrome_table") in {"checked", "complete"}:
        return "syndrome_extraction"
    if scope.get("stabilizer_commutation") in {"checked", "complete"}:
        return "stabilizer_commutation"
    if scope.get("correction_table") in {"checked", "complete"}:
        return "decoder_correctness"
    if scope.get("logical_preservation_small_code") in {"checked", "complete", "assumed"}:
        return "logical_preservation"
    return "logical_preservation"

def _validate_qec_witness_file(claim_dir: Path, spec: dict[str, Any] | None = None) -> list[str]:
    witness_path = claim_dir / "expected" / "qec_witness.json"
    if not witness_path.is_file():
        return []
    try:
        witness = json.loads(witness_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"expected/qec_witness.json invalid JSON: {exc}"]
    from qspecbench.qec_witness import validate_qec_witness

    claim_kind: str | None = None
    if spec is not None:
        claim_kind = _infer_qec_witness_claim_kind(spec)
    return validate_qec_witness(witness, claim_dir, claim_kind=claim_kind)

def _validate_qec_claim_scope(spec: dict[str, Any], claim_dir: Path) -> list[str]:
    errors: list[str] = []
    if spec.get("track") != "qec":
        return errors
    scope = spec.get("qec_claim_scope")
    if not scope:
        return errors

    if scope.get("stabilizer_commutation") == "checked":
        has_lean = any(
            e.get("type") == "lean_proof" and e.get("status") == "passing"
            for e in spec.get("evidence", [])
        )
        if not has_lean:
            errors.append(
                "qec_claim_scope.stabilizer_commutation checked requires passing lean_proof evidence"
            )

    distance = scope.get("distance") or {}
    if distance.get("status") == "checked":
        has_distance_evidence = False
        cert_level = scope.get("qec_certificate_level")
        for ev in spec.get("evidence", []):
            if ev.get("status") != "passing":
                continue
            path = claim_dir / ev.get("path", "")
            if not path.is_file():
                continue
            if ev.get("type") == "qec_verifier_result":
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                    if payload.get("distance_result"):
                        has_distance_evidence = True
                except json.JSONDecodeError as exc:
                    errors.append(f"invalid JSON in qec evidence {ev.get('path')}: {exc}")
        if not has_distance_evidence:
            errors.append(
                "qec_claim_scope.distance.status checked requires distance_result evidence "
                "from QEC adapter bruteforce run"
            )
        if cert_level == "qec_external_certificate_checked":
            has_smt = any(
                e.get("type") == "smt_certificate" and e.get("status") == "passing"
                for e in spec.get("evidence", [])
            )
            if not has_smt:
                errors.append(
                    "qec_certificate_level=qec_external_certificate_checked requires "
                    "passing smt_certificate evidence"
                )
    return errors

infer_qec_witness_claim_kind = _infer_qec_witness_claim_kind
validate_qec_witness_file = _validate_qec_witness_file
validate_qec_claim_scope = _validate_qec_claim_scope


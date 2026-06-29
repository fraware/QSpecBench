"""Validate external QEC certificate envelopes (scalable prover format).

Schema validation lives in artifact_schemas.py; this module adds semantic checks:
artifact SHA256 linkage, benchmark identity, and honest status bounds for stub certs.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _provenance_sha256(claim_dir: Path, artifact_path: str) -> str | None:
    prov_path = claim_dir / "expected" / "provenance.json"
    if not prov_path.is_file():
        return None
    try:
        provenance = json.loads(prov_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    for art in provenance.get("artifacts", []):
        if art.get("path") == artifact_path:
            return art.get("sha256")
    return None


def validate_qec_external_certificate(
    cert: dict[str, Any],
    claim_dir: Path,
    spec: dict[str, Any],
) -> list[str]:
    """Semantic validation beyond JSON Schema (fail-closed on stub over-claim)."""
    errors: list[str] = []
    code_ref = cert.get("code_ref") or {}
    artifact_path = code_ref.get("artifact_path")
    cert_sha = code_ref.get("artifact_sha256")
    if not cert_sha:
        errors.append("qec_external_certificate.code_ref.artifact_sha256 is required")
        return errors

    if artifact_path:
        artifact = claim_dir / artifact_path
        if artifact.is_file():
            import hashlib

            on_disk = hashlib.sha256(artifact.read_bytes()).hexdigest()
            if on_disk != cert_sha:
                errors.append(
                    "qec_external_certificate code_ref.artifact_sha256 does not match "
                    f"on-disk {artifact_path}"
                )
        prov_sha = _provenance_sha256(claim_dir, artifact_path)
        if prov_sha and prov_sha != cert_sha:
            errors.append(
                "qec_external_certificate code_ref.artifact_sha256 does not match "
                "expected/provenance.json"
            )

    bench_id = spec.get("id")
    if bench_id and code_ref.get("benchmark_id") and code_ref["benchmark_id"] != bench_id:
        errors.append(
            f"qec_external_certificate code_ref.benchmark_id {code_ref['benchmark_id']!r} "
            f"!= spec id {bench_id!r}"
        )

    result = cert.get("result") or {}
    status = result.get("status")
    if status == "proved" and cert.get("certificate_version", "").endswith("-stub"):
        errors.append(
            "qec_external_certificate with certificate_version stub cannot claim result.status=proved"
        )

    prover = cert.get("prover") or {}
    if prover.get("method") == "schema_only" and status not in {None, "unknown"}:
        errors.append(
            "schema_only prover method requires result.status unknown or absent"
        )

    witness = result.get("witness")
    if witness is not None and not isinstance(witness, dict):
        errors.append("qec_external_certificate.result.witness must be an object")
    elif isinstance(witness, dict):
        from qspecbench.qec_witness import validate_witness_fields

        errors.extend(validate_witness_fields(witness))
        errors.extend(_validate_witness(witness, result, cert, claim_dir))

    return errors


def _validate_witness(
    witness: dict[str, Any],
    result: dict[str, Any],
    cert: dict[str, Any],
    claim_dir: Path,
) -> list[str]:
    """Cross-check witness fields against result and claim_kind (fail-closed)."""
    errors: list[str] = []
    kind = cert.get("claim_kind")
    status = result.get("status")

    if status == "proved" and not witness.get("proof_artifact_sha256"):
        errors.append(
            "result.status=proved requires witness.proof_artifact_sha256 for external certificates"
        )

    computed = result.get("computed_value")
    if computed is not None and "min_distance" in witness:
        if witness["min_distance"] != computed:
            errors.append(
                "witness.min_distance does not match result.computed_value"
            )

    if kind == "minimum_distance":
        md = witness.get("min_distance")
        if md is not None and not isinstance(md, int):
            errors.append("witness.min_distance must be an integer")
    if witness.get("method") == "lookup_table" and not witness.get("complete_for"):
        errors.append("lookup_table witness requires complete_for scope declaration")

    if witness.get("method") == "bruteforce_weight_enumeration":
        complete = witness.get("complete_for")
        if not complete:
            errors.append(
                "bruteforce witness requires complete_for scope declaration"
            )

    if witness.get("over_claim") is True:
        errors.append("witness.over_claim must not be true")

    if kind == "stabilizer_commutation" and witness.get("commutes") is True:
        if status == "proved" and not witness.get("proof_artifact_sha256"):
            errors.append(
                "stabilizer_commutation witness with commutes=true and status=proved "
                "requires proof_artifact_sha256"
            )

    if witness.get("syndrome_table_sha256") and not isinstance(witness["syndrome_table_sha256"], str):
        errors.append("witness.syndrome_table_sha256 must be a hex string")

    from qspecbench.qec_witness import verify_witness_table_hashes

    errors.extend(verify_witness_table_hashes(witness, claim_dir))

    return errors


def validate_qec_external_certificate_path(
    path: Path,
    claim_dir: Path,
    spec: dict[str, Any],
) -> list[str]:
    try:
        cert = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path.name}: invalid JSON: {exc}"]
    return validate_qec_external_certificate(cert, claim_dir, spec)

"""Small-code QEC witness helpers (syndrome table hash export)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

CLAIM_KIND_ALLOWED_METHODS: dict[str, frozenset[str]] = {
    "minimum_distance": frozenset({"bruteforce_weight_enumeration", "schema_only"}),
    "logical_preservation": frozenset({"lookup_table", "schema_only"}),
    "decoder_correctness": frozenset({"lookup_table", "schema_only"}),
    "syndrome_extraction": frozenset({"lookup_table", "schema_only"}),
    "stabilizer_commutation": frozenset({"schema_only", "bruteforce_weight_enumeration"}),
}


def _canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def syndrome_table_sha256(table: dict[str, Any]) -> str:
    """Stable SHA-256 of a syndrome_table.json payload for witness envelopes."""
    return hashlib.sha256(_canonical_json_bytes(table)).hexdigest()


def correction_table_sha256(table: dict[str, Any]) -> str:
    """Stable SHA-256 of a correction_table.json payload."""
    return hashlib.sha256(_canonical_json_bytes(table)).hexdigest()


def _resolve_artifact_path(claim_dir: Path, relative_path: str) -> Path:
    direct = claim_dir / relative_path
    if direct.is_file():
        return direct
    return claim_dir / "artifacts" / relative_path


def validate_witness_fields(
    witness: dict[str, Any],
    *,
    claim_kind: str | None = None,
) -> list[str]:
    """Semantic validation for QEC witness envelopes (beyond JSON Schema)."""
    errors: list[str] = []
    if not witness.get("complete_for"):
        errors.append("witness.complete_for is required")

    method = witness.get("method")
    if claim_kind and method:
        allowed = CLAIM_KIND_ALLOWED_METHODS.get(claim_kind)
        if allowed is not None and method not in allowed:
            errors.append(
                f"witness.method {method!r} incompatible with claim_kind {claim_kind!r}"
            )

    if witness.get("syndrome_table_sha256") and not witness.get("syndrome_table_path"):
        errors.append("witness.syndrome_table_path is required when syndrome_table_sha256 is set")
    if witness.get("correction_table_sha256") and not witness.get("correction_table_path"):
        errors.append(
            "witness.correction_table_path is required when correction_table_sha256 is set"
        )
    return errors


def verify_witness_table_hashes(
    witness: dict[str, Any],
    claim_dir: Path,
) -> list[str]:
    """Verify syndrome/correction table hashes against on-disk artifact files."""
    errors: list[str] = []
    syndrome_path = witness.get("syndrome_table_path")
    expected_syndrome = witness.get("syndrome_table_sha256")
    if expected_syndrome:
        if not syndrome_path:
            errors.append("witness.syndrome_table_path is required when syndrome_table_sha256 is set")
        else:
            artifact = _resolve_artifact_path(claim_dir, syndrome_path)
            if not artifact.is_file():
                errors.append(f"witness syndrome table artifact missing: {syndrome_path}")
            else:
                table = json.loads(artifact.read_text(encoding="utf-8"))
                actual = syndrome_table_sha256(table)
                if actual != expected_syndrome:
                    errors.append(
                        f"witness.syndrome_table_sha256 mismatch for {syndrome_path}"
                    )

    correction_path = witness.get("correction_table_path")
    expected_correction = witness.get("correction_table_sha256")
    if expected_correction:
        if not correction_path:
            errors.append(
                "witness.correction_table_path is required when correction_table_sha256 is set"
            )
        else:
            artifact = _resolve_artifact_path(claim_dir, correction_path)
            if not artifact.is_file():
                errors.append(f"witness correction table artifact missing: {correction_path}")
            else:
                table = json.loads(artifact.read_text(encoding="utf-8"))
                actual = correction_table_sha256(table)
                if actual != expected_correction:
                    errors.append(
                        f"witness.correction_table_sha256 mismatch for {correction_path}"
                    )
    return errors


def validate_qec_witness(
    witness: dict[str, Any],
    claim_dir: Path,
    *,
    claim_kind: str | None = None,
) -> list[str]:
    """Deep validation: fields, claim_kind/method pairing, and on-disk table hashes."""
    errors = validate_witness_fields(witness, claim_kind=claim_kind)
    errors.extend(verify_witness_table_hashes(witness, claim_dir))
    return errors


def export_small_code_witness(
    *,
    syndrome_table_path: Path,
    correction_table_path: Path | None = None,
    method: str = "lookup_table",
    complete_for: str,
) -> dict[str, Any]:
    """Build witness JSON fragment with syndrome_table_sha256 for external certificates."""
    table = json.loads(syndrome_table_path.read_text(encoding="utf-8"))
    witness: dict[str, Any] = {
        "method": method,
        "complete_for": complete_for,
        "syndrome_table_sha256": syndrome_table_sha256(table),
        "syndrome_table_path": syndrome_table_path.name,
    }
    if correction_table_path is not None and correction_table_path.is_file():
        correction = json.loads(correction_table_path.read_text(encoding="utf-8"))
        witness["correction_table_sha256"] = correction_table_sha256(correction)
        witness["correction_table_path"] = correction_table_path.name
    return witness

"""Small-code QEC witness helpers (syndrome table hash export)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def _canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def syndrome_table_sha256(table: dict[str, Any]) -> str:
    """Stable SHA-256 of a syndrome_table.json payload for witness envelopes."""
    return hashlib.sha256(_canonical_json_bytes(table)).hexdigest()


def correction_table_sha256(table: dict[str, Any]) -> str:
    """Stable SHA-256 of a correction_table.json payload."""
    return hashlib.sha256(_canonical_json_bytes(table)).hexdigest()


def verify_witness_table_hashes(
    witness: dict[str, Any],
    claim_dir: Path,
) -> list[str]:
    """Verify syndrome/correction table hashes against on-disk artifact files."""
    errors: list[str] = []
    syndrome_path = witness.get("syndrome_table_path")
    expected_syndrome = witness.get("syndrome_table_sha256")
    if expected_syndrome and syndrome_path:
        artifact = claim_dir / "artifacts" / syndrome_path
        if not artifact.is_file():
            artifact = claim_dir / syndrome_path
        if artifact.is_file():
            table = json.loads(artifact.read_text(encoding="utf-8"))
            actual = syndrome_table_sha256(table)
            if actual != expected_syndrome:
                errors.append(
                    f"witness.syndrome_table_sha256 mismatch for {syndrome_path}"
                )
        else:
            errors.append(f"witness syndrome table artifact missing: {syndrome_path}")

    correction_path = witness.get("correction_table_path")
    expected_correction = witness.get("correction_table_sha256")
    if expected_correction and correction_path:
        artifact = claim_dir / "artifacts" / correction_path
        if not artifact.is_file():
            artifact = claim_dir / correction_path
        if artifact.is_file():
            table = json.loads(artifact.read_text(encoding="utf-8"))
            actual = correction_table_sha256(table)
            if actual != expected_correction:
                errors.append(
                    f"witness.correction_table_sha256 mismatch for {correction_path}"
                )
        else:
            errors.append(f"witness correction table artifact missing: {correction_path}")
    return errors


def export_small_code_witness(
    *,
    syndrome_table_path: Path,
    correction_table_path: Path | None = None,
    method: str = "lookup_table",
    complete_for: str | None = None,
) -> dict[str, Any]:
    """Build witness JSON fragment with syndrome_table_sha256 for external certificates."""
    table = json.loads(syndrome_table_path.read_text(encoding="utf-8"))
    witness: dict[str, Any] = {
        "method": method,
        "syndrome_table_sha256": syndrome_table_sha256(table),
        "syndrome_table_path": syndrome_table_path.name,
    }
    if complete_for:
        witness["complete_for"] = complete_for
    if correction_table_path is not None and correction_table_path.is_file():
        correction = json.loads(correction_table_path.read_text(encoding="utf-8"))
        witness["correction_table_sha256"] = correction_table_sha256(correction)
        witness["correction_table_path"] = correction_table_path.name
    return witness

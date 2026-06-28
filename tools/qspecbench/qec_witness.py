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
        witness["correction_table_sha256"] = hashlib.sha256(
            _canonical_json_bytes(correction)
        ).hexdigest()
        witness["correction_table_path"] = correction_table_path.name
    return witness

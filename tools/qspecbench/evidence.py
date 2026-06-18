"""Evidence helpers."""

from __future__ import annotations

from typing import Any


def list_evidence_types(spec: dict[str, Any]) -> set[str]:
    types: set[str] = set()
    for entry in spec.get("acceptable_evidence", []):
        types.add(entry.get("type", ""))
    for entry in spec.get("evidence", []):
        types.add(entry.get("type", ""))
    types.discard("")
    return types

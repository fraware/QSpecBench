"""Claim-local typed evidence adapter bindings.

The sidecar exists to migrate historical schema-0.3 specs without using the descriptive
``checker`` string as executable configuration.  New specs should prefer an explicit stable
``adapter`` id on the evidence entry once the main schema adopts the typed protocol directly.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from qspecbench.typed_adapter_registry import get_typed_adapter

SIDECAR = "evidence_adapters.json"
SIDECAR_SCHEMA = "qspecbench.evidence_adapter_bindings.v1"


def load_evidence_adapter_bindings(claim_dir: Path) -> dict[str, str]:
    path = claim_dir / SIDECAR
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema") != SIDECAR_SCHEMA:
        raise ValueError(f"{SIDECAR}: invalid or missing schema id")
    if payload.get("benchmark_id") != claim_dir.name:
        raise ValueError(f"{SIDECAR}: benchmark_id must equal claim directory name")
    bindings = payload.get("bindings")
    if not isinstance(bindings, dict):
        raise ValueError(f"{SIDECAR}: bindings must be an object")
    out: dict[str, str] = {}
    for evidence_id, adapter_id in bindings.items():
        if not isinstance(evidence_id, str) or not evidence_id:
            raise ValueError(f"{SIDECAR}: evidence id must be a non-empty string")
        if not isinstance(adapter_id, str) or get_typed_adapter(adapter_id) is None:
            raise ValueError(f"{SIDECAR}: unknown typed adapter id {adapter_id!r}")
        out[evidence_id] = adapter_id
    return out


def bound_adapter_id(entry: dict[str, Any], claim_dir: Path) -> str | None:
    """Return one authoritative adapter id, rejecting spec/sidecar disagreement."""
    entry_adapter = entry.get("adapter")
    sidecar_adapter = load_evidence_adapter_bindings(claim_dir).get(str(entry.get("id")))
    if entry_adapter and sidecar_adapter and entry_adapter != sidecar_adapter:
        raise ValueError(
            f"evidence {entry.get('id')!r}: spec adapter {entry_adapter!r} conflicts with "
            f"{SIDECAR} binding {sidecar_adapter!r}"
        )
    return str(entry_adapter or sidecar_adapter) if (entry_adapter or sidecar_adapter) else None


def validate_evidence_adapter_bindings_sidecar(
    spec: dict[str, Any], claim_dir: Path
) -> list[str]:
    """Validate sidecar identity, evidence references and adapter/evidence compatibility."""
    try:
        bindings = load_evidence_adapter_bindings(claim_dir)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [str(exc)]
    if not bindings:
        return []

    evidence = {str(item.get("id")): item for item in spec.get("evidence", []) if item.get("id")}
    errors: list[str] = []
    for evidence_id, adapter_id in bindings.items():
        entry = evidence.get(evidence_id)
        if entry is None:
            errors.append(f"{SIDECAR}: binding references unknown evidence id {evidence_id!r}")
            continue
        typed = get_typed_adapter(adapter_id)
        assert typed is not None
        evidence_type = str(entry.get("type", ""))
        if evidence_type not in typed.supported_evidence_types:
            errors.append(
                f"{SIDECAR}: {adapter_id} does not support evidence type {evidence_type!r} "
                f"for {evidence_id!r}"
            )
        entry_adapter = entry.get("adapter")
        if entry_adapter and entry_adapter != adapter_id:
            errors.append(
                f"{SIDECAR}: binding for {evidence_id!r} conflicts with spec adapter {entry_adapter!r}"
            )
    return errors

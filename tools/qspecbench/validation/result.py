"""Validation result types and spec loading."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ValidationResult:
    spec_path: Path
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _apply_typed_evidence_bindings(data: dict[str, Any], spec_path: Path) -> None:
    """Overlay migration sidecar bindings without changing historical YAML on disk.

    Existing explicit ``adapter`` values win here; validation separately rejects a conflict with
    the sidecar.  The runner therefore receives typed execution identity without consulting the
    descriptive ``checker`` field.
    """
    from qspecbench.evidence_adapter_bindings import load_evidence_adapter_bindings

    bindings = load_evidence_adapter_bindings(spec_path.parent)
    if not bindings:
        return
    for entry in data.get("evidence", []) or []:
        evidence_id = str(entry.get("id", ""))
        if evidence_id in bindings and not entry.get("adapter"):
            entry["adapter"] = bindings[evidence_id]


def load_spec(spec_path: Path) -> dict[str, Any]:
    with spec_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if data is None:
        raise ValueError(f"Empty or invalid YAML in {spec_path}")
    _apply_typed_evidence_bindings(data, spec_path)
    return data

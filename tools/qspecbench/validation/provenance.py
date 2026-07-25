"""Provenance validation wiring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qspecbench.provenance import validate_provenance


def validate_provenance_rules(spec: dict[str, Any], claim_dir: Path) -> list[str]:
    return validate_provenance(spec, claim_dir)

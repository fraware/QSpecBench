# -*- coding: utf-8 -*-
"""Fail-closed Stim-compatible detector-error-model (DEM) adapter for QEC fragment.

Does **not** invoke Stim/PyMatching. Validates a declared DEM JSON artifact by schema
+ SHA-256, and optionally checks that declared in-model faults are listed.
Never treats a bare success string as a certificate.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


REQUIRED_DEM_KEYS = (
    "schema",
    "name",
    "detectors",
    "rounds",
    "in_model_faults",
    "outside_negatives",
    "decode_rule",
)


class StimDemAdapterError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_stim_compatible_dem(
    dem_path: Path,
    *,
    expected_sha256: str | None = None,
) -> dict[str, Any]:
    """Load and fail-closed-validate a Stim-compatible DEM JSON fragment."""
    if not dem_path.is_file():
        raise StimDemAdapterError(f"DEM artifact missing: {dem_path}")
    actual = sha256_file(dem_path)
    if expected_sha256 is not None and actual != expected_sha256:
        raise StimDemAdapterError(
            f"DEM sha256 mismatch: expected {expected_sha256}, got {actual}"
        )
    try:
        payload = json.loads(dem_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StimDemAdapterError(f"DEM JSON parse failed: {exc}") from exc
    if not isinstance(payload, dict):
        raise StimDemAdapterError("DEM root must be an object")
    for key in REQUIRED_DEM_KEYS:
        if key not in payload:
            raise StimDemAdapterError(f"DEM missing required key {key!r}")
    if payload.get("schema") != "qspecbench.stim_compatible_dem.v1":
        raise StimDemAdapterError(
            f"unexpected DEM schema {payload.get('schema')!r}; "
            "expected qspecbench.stim_compatible_dem.v1"
        )
    if payload.get("full_spacetime_mwpm") is True:
        raise StimDemAdapterError(
            "DEM must not claim full_spacetime_mwpm=true without Stim/Blossom evidence"
        )
    if "stim_command" in payload and not payload.get("stim_output_sha256"):
        raise StimDemAdapterError(
            "stim_command present without stim_output_sha256 (fail-closed)"
        )
    return {
        "ok": True,
        "path": str(dem_path),
        "sha256": actual,
        "name": payload.get("name"),
        "in_model_faults": list(payload.get("in_model_faults") or []),
        "outside_negatives": list(payload.get("outside_negatives") or []),
        "notes": payload.get("notes"),
    }

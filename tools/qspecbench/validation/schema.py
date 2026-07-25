"""Schema dialect and OpenQASM profile validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

from qspecbench.schema import SCHEMA_DIR
from qspecbench.schema_dialect import validate_schema_dialect

ARTIFACT_BOUND_LEVEL = "artifact_bound_reference_claim"


def validate_schema_rules(spec: dict[str, Any]) -> list[str]:
    return validate_schema_dialect(spec)


def validate_openqasm_profile(spec: dict[str, Any], claim_dir: Path) -> list[str]:
    """Require a declared OpenQASM profile for QASM-backed promoted / kernel bridges."""
    errors: list[str] = []
    has_qasm = any(
        obj.get("format") in {"qasm2", "qasm3"} and obj.get("path")
        for obj in spec.get("objects", [])
    )
    maturity = (spec.get("status") or {}).get("maturity")
    profile = spec.get("openqasm_profile")
    if not has_qasm:
        return errors
    if maturity in {ARTIFACT_BOUND_LEVEL, "reference_claim"} and not profile:
        errors.append(
            f"{maturity} with QASM artifacts requires openqasm_profile "
            "(see schema/profiles/)"
        )
        return errors
    if not profile:
        return errors

    profile_path = SCHEMA_DIR / "profiles" / f"{profile}.json"
    schema_path = SCHEMA_DIR / "openqasm_profile.schema.json"
    if not profile_path.is_file():
        errors.append(f"openqasm_profile {profile!r}: missing {profile_path}")
        return errors
    try:
        payload = json.loads(profile_path.read_text(encoding="utf-8"))
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(payload)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"openqasm_profile {profile!r} invalid: {exc}")
        return errors
    if payload.get("id") != profile:
        errors.append(
            f"openqasm_profile file id {payload.get('id')!r} != declared {profile!r}"
        )
    _ = claim_dir
    return errors

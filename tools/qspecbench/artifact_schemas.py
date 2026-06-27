"""Validate expected/*.json artifacts against schema/*.schema.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

from qspecbench.schema import REPO_ROOT

SCHEMA_DIR = REPO_ROOT / "schema"

# Map artifact filename (or object name hint) to JSON Schema file.
ARTIFACT_SCHEMAS: dict[str, Path] = {
    "semantic_bridge.json": SCHEMA_DIR / "semantic_bridge.schema.json",
    "provenance.json": SCHEMA_DIR / "provenance.schema.json",
    "code.json": SCHEMA_DIR / "qec_code.schema.json",
    "syndrome_table.json": SCHEMA_DIR / "syndrome_table.schema.json",
    "correction_table.json": SCHEMA_DIR / "correction_table.schema.json",
    "error_model.json": SCHEMA_DIR / "error_model.schema.json",
    "channel.json": SCHEMA_DIR / "channel.schema.json",
    "resource_contract.json": SCHEMA_DIR / "resource_contract.schema.json",
    "bridge_verify.result.json": SCHEMA_DIR / "bridge_result.schema.json",
    "qec_external_certificate.json": SCHEMA_DIR / "qec_external_certificate.schema.json",
}

# Optional: object `name` in spec.yaml may disambiguate generic paths.
OBJECT_NAME_SCHEMAS: dict[str, Path] = {
    "hamiltonian": SCHEMA_DIR / "hamiltonian.schema.json",
    "code": SCHEMA_DIR / "qec_code.schema.json",
    "syndrome_table": SCHEMA_DIR / "syndrome_table.schema.json",
    "correction_table": SCHEMA_DIR / "correction_table.schema.json",
    "semantic_bridge": SCHEMA_DIR / "semantic_bridge.schema.json",
    "provenance": SCHEMA_DIR / "provenance.schema.json",
    "error_model": SCHEMA_DIR / "error_model.schema.json",
    "channel": SCHEMA_DIR / "channel.schema.json",
    "resource_contract": SCHEMA_DIR / "resource_contract.schema.json",
}

_schema_cache: dict[Path, dict[str, Any]] = {}


def _load_artifact_schema(path: Path) -> dict[str, Any]:
    if path not in _schema_cache:
        _schema_cache[path] = json.loads(path.read_text(encoding="utf-8"))
    return _schema_cache[path]


def schema_for_artifact(rel_path: str, obj_name: str | None = None) -> Path | None:
    basename = Path(rel_path).name
    if basename in ARTIFACT_SCHEMAS:
        return ARTIFACT_SCHEMAS[basename]
    if obj_name and obj_name in OBJECT_NAME_SCHEMAS:
        return OBJECT_NAME_SCHEMAS[obj_name]
    return None


def validate_json_artifact(path: Path, schema_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path.name}: invalid JSON: {exc}"]
    # Legacy hamiltonian artifacts without top-level `type` are rejected (corpus v0.2.0).
    schema = _load_artifact_schema(schema_path)
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as exc:
        errors.append(f"{path.name}: schema {schema_path.name}: {exc.message}")
    return errors


def validate_claim_artifacts(spec: dict[str, Any], claim_dir: Path) -> list[str]:
    """Validate on-disk JSON artifacts declared in spec.objects and expected/."""
    errors: list[str] = []
    seen: set[Path] = set()

    for ev in spec.get("evidence", []):
        rel = ev.get("path")
        if not rel or not str(rel).endswith(".json"):
            continue
        path = claim_dir / rel
        if not path.is_file():
            continue
        if path.name == "qec_external_certificate.json" or ev.get("type") == "qec_external_certificate":
            schema_path = SCHEMA_DIR / "qec_external_certificate.schema.json"
            if schema_path.is_file():
                resolved = path.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    errors.extend(validate_json_artifact(path, schema_path))
            continue
        schema_path = schema_for_artifact(rel, None)
        if schema_path is None or not schema_path.is_file():
            continue
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        errors.extend(validate_json_artifact(path, schema_path))

    for obj in spec.get("objects", []):
        rel = obj.get("path")
        if not rel or not str(rel).endswith(".json"):
            continue
        path = claim_dir / rel
        if not path.is_file():
            continue
        schema_path = schema_for_artifact(rel, obj.get("name"))
        if schema_path is None or not schema_path.is_file():
            continue
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        errors.extend(validate_json_artifact(path, schema_path))

    expected = claim_dir / "expected"
    if expected.is_dir():
        for rel_name, schema_path in ARTIFACT_SCHEMAS.items():
            path = expected / rel_name
            if not path.is_file():
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            errors.extend(validate_json_artifact(path, schema_path))

    return errors

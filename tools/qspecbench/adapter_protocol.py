"""Typed request/result contract for external evidence adapters.

This module is intentionally transport-agnostic. Adapters may run locally, in CI, or in an
isolated environment, but they must exchange versioned JSON-compatible payloads that bind
benchmark, proposition, semantics, inputs, obligations, tool identity and trust class.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

REQUEST_SCHEMA = "adapter_request.schema.json"
RESULT_SCHEMA = "adapter_result.schema.json"


def _repo_root(start: Path) -> Path:
    probe = start.resolve()
    for candidate in (probe, *probe.parents):
        if (candidate / "schema" / REQUEST_SCHEMA).is_file():
            return candidate
    raise FileNotFoundError("could not locate QSpecBench schema directory")


def _schema(start: Path, name: str) -> dict[str, Any]:
    root = _repo_root(start)
    return json.loads((root / "schema" / name).read_text(encoding="utf-8"))


def validate_adapter_request(payload: dict[str, Any], start: Path) -> list[str]:
    """Return validation errors for an AdapterRequest payload."""
    errors: list[str] = []
    try:
        jsonschema.validate(payload, _schema(start, REQUEST_SCHEMA))
    except jsonschema.ValidationError as exc:
        errors.append(f"adapter request schema: {exc.message}")
    return errors


def validate_adapter_result(
    payload: dict[str, Any], start: Path, request: dict[str, Any] | None = None
) -> list[str]:
    """Validate AdapterResult and, when supplied, bind it to the originating request."""
    errors: list[str] = []
    try:
        jsonschema.validate(payload, _schema(start, RESULT_SCHEMA))
    except jsonschema.ValidationError as exc:
        errors.append(f"adapter result schema: {exc.message}")
        return errors

    if request is None:
        return errors

    for key in ("adapter_id", "adapter_version", "benchmark_id", "proposition_id", "semantic_profile_id"):
        if payload.get(key) != request.get(key):
            errors.append(f"adapter result {key} does not match request")

    requested = set(request.get("requested_obligations") or [])
    supported = set(payload.get("supported_obligations") or [])
    if not supported.issubset(requested):
        errors.append(
            "adapter result claims obligations that were not requested: "
            + ", ".join(sorted(supported - requested))
        )

    request_hashes = {item.get("sha256") for item in request.get("inputs", []) if item.get("sha256")}
    result_hashes = set(payload.get("input_hashes") or [])
    if result_hashes != request_hashes:
        errors.append("adapter result input_hashes do not exactly match request inputs")

    if payload.get("status") == "passing" and not supported:
        errors.append("passing adapter result must support at least one requested obligation")
    return errors


def load_and_validate_pair(request_path: Path, result_path: Path) -> list[str]:
    request = json.loads(request_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    errors = validate_adapter_request(request, request_path)
    errors.extend(validate_adapter_result(result, result_path, request=request))
    return errors

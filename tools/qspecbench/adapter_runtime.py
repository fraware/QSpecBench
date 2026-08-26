"""Runtime binding for the typed AdapterRequest/AdapterResult protocol.

Assurance-backed execution is bound fail-closed to proposition, semantic profile, obligations,
input hashes, adapter identity, trust class, typed dependencies/outputs and runner limits.
Legacy adapter stdout may be normalized during migration, but runner-observed execution metadata
is injected by QSpecBench and may not be asserted by the adapter subprocess itself.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from qspecbench.adapter_protocol import validate_adapter_request, validate_adapter_result
from qspecbench.semantic_profiles import ProfileError, graph_profile_binding
from qspecbench.typed_adapter_registry import (
    get_typed_adapter,
    proof_assistant_native_checked_is_kernel_subtype,
)

GRAPH_FILENAME = "assurance_graph.yaml"


class AdapterRuntimeError(ValueError):
    """Raised when an assurance-backed adapter execution cannot be bound exactly."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_sha256(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _load_graph(claim_dir: Path) -> dict[str, Any] | None:
    graph_path = claim_dir / GRAPH_FILENAME
    if not graph_path.is_file():
        return None
    try:
        graph = yaml.safe_load(graph_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise AdapterRuntimeError(f"cannot load assurance graph: {exc}") from exc
    if not isinstance(graph, dict):
        raise AdapterRuntimeError("assurance graph must contain a mapping")
    return graph


def assurance_edge_for_evidence(claim_dir: Path, evidence_id: str) -> dict[str, Any] | None:
    graph = _load_graph(claim_dir)
    if graph is None:
        return None
    matching_edges = [
        edge
        for edge in graph.get("evidence_edges", []) or []
        if isinstance(edge, dict) and edge.get("evidence_id") == evidence_id
    ]
    if len(matching_edges) > 1:
        raise AdapterRuntimeError(
            f"assurance graph contains duplicate evidence edges for {evidence_id!r}"
        )
    return matching_edges[0] if matching_edges else None


def _relative_input(claim_dir: Path, path: Path, role: str) -> dict[str, Any]:
    resolved_claim = claim_dir.resolve()
    resolved_path = path.resolve()
    try:
        rel = resolved_path.relative_to(resolved_claim)
    except ValueError as exc:
        raise AdapterRuntimeError(f"adapter input escapes claim directory: {resolved_path}") from exc
    if not resolved_path.is_file():
        raise AdapterRuntimeError(f"adapter input is not a file: {rel.as_posix()}")
    return {"path": rel.as_posix(), "sha256": _sha256(resolved_path), "role": role}


def build_adapter_request(
    entry: dict[str, Any],
    claim_dir: Path,
    *,
    adapter_id: str,
    artifact: Path | None,
    secondary: Path | None = None,
    limits: dict[str, int] | None = None,
) -> dict[str, Any] | None:
    """Build and validate the request for the entry's authoritative assurance edge."""
    evidence_id = str(entry.get("id") or "")
    if not evidence_id:
        raise AdapterRuntimeError("evidence entry has no id")
    edge = assurance_edge_for_evidence(claim_dir, evidence_id)
    if edge is None:
        return None

    graph_adapter = edge.get("adapter_id")
    if not graph_adapter:
        raise AdapterRuntimeError(
            f"assurance graph evidence edge {evidence_id!r} must declare adapter_id"
        )
    if graph_adapter != adapter_id:
        raise AdapterRuntimeError(
            f"runtime adapter {adapter_id!r} contradicts assurance edge adapter_id "
            f"{graph_adapter!r} for {evidence_id!r}"
        )

    typed = get_typed_adapter(adapter_id)
    if typed is None:
        raise AdapterRuntimeError(
            f"assurance-backed execution requires a known typed adapter: {adapter_id!r}"
        )

    edge_trust = edge.get("trust_class")
    if edge_trust != typed.trust_ceiling:
        raise AdapterRuntimeError(
            f"assurance edge trust_class {edge_trust!r} does not exactly match registered "
            f"trust class {typed.trust_ceiling!r} for {adapter_id!r}"
        )

    graph = _load_graph(claim_dir)
    if graph is None:
        raise AdapterRuntimeError("assurance graph disappeared during request construction")
    proposition = graph.get("proposition") or {}
    semantic_profile = graph.get("semantic_profile") or {}
    proposition_id = proposition.get("id")
    semantic_profile_id = semantic_profile.get("id")
    benchmark_id = graph.get("benchmark_id")
    if not benchmark_id or not proposition_id or not semantic_profile_id:
        raise AdapterRuntimeError(
            "assurance-backed execution requires benchmark_id, proposition.id and semantic_profile.id"
        )

    requested = edge.get("supports") or []
    if (
        not isinstance(requested, list)
        or not requested
        or not all(isinstance(item, str) and item for item in requested)
    ):
        raise AdapterRuntimeError(
            f"assurance edge {evidence_id!r} must declare one or more supported obligations"
        )

    dependencies = edge.get("depends_on") or []
    expected_outputs = edge.get("expected_outputs") or []
    if not isinstance(dependencies, list) or not all(
        isinstance(item, str) and item for item in dependencies
    ):
        raise AdapterRuntimeError(f"assurance edge {evidence_id!r} has invalid depends_on")
    if not isinstance(expected_outputs, list) or not all(
        isinstance(item, str) and item for item in expected_outputs
    ):
        raise AdapterRuntimeError(f"assurance edge {evidence_id!r} has invalid expected_outputs")

    profile_binding = {"content_sha256": None, "content_version": None}
    try:
        profile_binding = graph_profile_binding(graph)
        if profile_binding["id"] != str(semantic_profile_id):
            raise AdapterRuntimeError(
                f"semantic profile id {semantic_profile_id!r} does not match bound "
                f"{profile_binding['id']!r}"
            )
    except ProfileError as exc:
        raise AdapterRuntimeError(str(exc)) from exc

    if artifact is None:
        raise AdapterRuntimeError(
            f"assurance-backed evidence {evidence_id!r} requires a concrete primary input path"
        )
    inputs = [_relative_input(claim_dir, artifact, "primary")]
    if secondary is not None:
        inputs.append(_relative_input(claim_dir, secondary, "secondary"))

    request: dict[str, Any] = {
        "schema": "qspecbench.adapter_request.v1",
        "adapter_id": typed.adapter_id,
        "adapter_version": typed.adapter_version,
        "benchmark_id": str(benchmark_id),
        "proposition_id": str(proposition_id),
        "semantic_profile_id": str(semantic_profile_id),
        "semantic_profile_sha256": profile_binding.get("content_sha256"),
        "semantic_profile_version": profile_binding.get("content_version"),
        "tool": {
            "name": typed.adapter_id,
            "version": typed.adapter_version,
            "digest": None,
        },
        "inputs": inputs,
        "requested_obligations": list(requested),
        "dependencies": list(dependencies),
        "expected_outputs": list(expected_outputs),
        "config": {
            "evidence_id": evidence_id,
            "evidence_type": str(entry.get("type") or ""),
        },
        "limits": dict(limits or {}),
    }
    errors = validate_adapter_request(request, claim_dir)
    if errors:
        raise AdapterRuntimeError("; ".join(errors))
    return request


def normalize_adapter_result(
    payload: dict[str, Any],
    claim_dir: Path,
    *,
    request: dict[str, Any],
    runner_execution: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a native typed result or normalize legacy adapter JSON fail-closed."""
    adapter_id = str(request["adapter_id"])
    typed = get_typed_adapter(adapter_id)
    if typed is None:
        raise AdapterRuntimeError(f"unknown typed adapter in request: {adapter_id!r}")

    raw_result_sha256 = _json_sha256(payload)

    if payload.get("schema") == "qspecbench.adapter_result.v1":
        if "runner_execution" in payload:
            raise AdapterRuntimeError(
                "adapter subprocess may not assert QSpecBench runner_execution metadata"
            )
        result = dict(payload)
        if result.get("result_sha256") is None:
            result["result_sha256"] = raw_result_sha256
    else:
        if payload.get("skipped"):
            status = "not_checked"
            supported: list[str] = []
        elif payload.get("ok") is True:
            status = "passing"
            supported = list(request.get("requested_obligations") or [])
        elif payload.get("ok") is False:
            status = "failing"
            supported = []
        else:
            raise AdapterRuntimeError(
                "legacy adapter JSON must declare ok=true/false or skipped=true before normalization"
            )

        notes = payload.get("notes") or payload.get("skip_reason")
        migration_note = (
            "Normalized by the QSpecBench runner from legacy adapter JSON; supported_obligations "
            "come from the validated assurance edge/request, not from legacy adapter-authored "
            "semantic obligation metadata."
        )
        if notes:
            migration_note = f"{migration_note} Adapter note: {notes}"

        result = {
            "schema": "qspecbench.adapter_result.v1",
            "adapter_id": typed.adapter_id,
            "adapter_version": typed.adapter_version,
            "benchmark_id": request["benchmark_id"],
            "proposition_id": request["proposition_id"],
            "semantic_profile_id": request["semantic_profile_id"],
            "status": status,
            "supported_obligations": supported,
            "trust_class": typed.trust_ceiling,
            "tool": {
                "name": str(payload.get("checker") or typed.adapter_id),
                "version": payload.get("tool_version"),
                "digest": payload.get("tool_digest") or payload.get("digest"),
            },
            "input_hashes": [item["sha256"] for item in request["inputs"]],
            "result_sha256": payload.get("result_sha256") or raw_result_sha256,
            "certificate_sha256": payload.get("certificate_sha256"),
            "started_at": payload.get("started_at"),
            "finished_at": payload.get("finished_at"),
            "notes": migration_note,
        }

    if runner_execution is not None:
        result["runner_execution"] = runner_execution

    claimed = result.get("trust_class")
    if claimed != typed.trust_ceiling and not proof_assistant_native_checked_is_kernel_subtype(
        str(claimed), typed.trust_ceiling
    ):
        raise AdapterRuntimeError(
            f"adapter result trust_class {claimed!r} does not exactly match "
            f"registered trust class {typed.trust_ceiling!r} for {adapter_id!r}"
        )

    errors = validate_adapter_result(result, claim_dir, request=request)
    if errors:
        raise AdapterRuntimeError("; ".join(errors))
    return result

"""Validation for optional typed assurance-graph sidecars.

The v1 sidecar is deliberately additive: legacy 0.3 benchmark specs remain readable,
while promoted claims are warned until they migrate. Once a sidecar exists, its
obligation/evidence closure is fail-closed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
import yaml

from qspecbench.maturity_policy import EXPERIMENTAL_CLOSED, cached_maturity_errors, derive_maturity
from qspecbench.semantic_profiles import cross_consistency_errors
from qspecbench.typed_adapter_registry import get_typed_adapter
from qspecbench.validation.review_attestations import validate_review_attestations

PROMOTED_MATURITIES = {"reference_claim", "artifact_bound_reference_claim"}
GRAPH_REQUIRED_MATURITIES = PROMOTED_MATURITIES | {EXPERIMENTAL_CLOSED}
GRAPH_FILENAME = "assurance_graph.yaml"
GRAPH_SCHEMA = "schema/assurance_graph.schema.json"
OPENQASM_PROFILE_SCHEMA = "schema/openqasm_profile.schema.json"
GENERIC_PROFILE_SCHEMA = "schema/semantic_profile.schema.json"


def _repo_root(start: Path) -> Path:
    probe = start.resolve()
    for candidate in (probe, *probe.parents):
        if (candidate / "schema" / "qspecbench.schema.json").is_file():
            return candidate
    return probe


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_profile(
    graph: dict[str, Any],
    root: Path,
    *,
    require_digest: bool = False,
) -> list[str]:
    errors: list[str] = []
    profile = graph.get("semantic_profile") or {}
    profile_id = profile.get("id")
    if not profile_id:
        return ["assurance graph semantic_profile.id is required"]

    profile_path = root / "schema" / "profiles" / f"{profile_id}.json"
    if not profile_path.is_file():
        return [f"assurance graph semantic profile does not exist: {profile_id}"]

    try:
        profile_doc = _load_json(profile_path)
        schema_name = (
            OPENQASM_PROFILE_SCHEMA
            if str(profile_id).startswith("qspecbench.openqasm3.")
            else GENERIC_PROFILE_SCHEMA
        )
        jsonschema.validate(profile_doc, _load_json(root / schema_name))
    except (OSError, json.JSONDecodeError, jsonschema.ValidationError) as exc:
        return [f"assurance graph semantic profile invalid: {profile_id}: {exc}"]

    if profile_doc.get("id") != profile_id:
        errors.append(f"semantic profile id mismatch: expected {profile_id}")

    import hashlib
    import json as json_lib

    actual_digest = hashlib.sha256(
        json_lib.dumps(profile_doc, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    declared_digest = profile.get("content_sha256") or profile.get("sha256")
    if declared_digest and declared_digest != actual_digest:
        errors.append("assurance graph semantic profile content_sha256 does not match registered profile")
    if require_digest and not declared_digest:
        errors.append("experimental_closed/promoted graphs must bind semantic profile content_sha256")
    if str(profile_id).startswith("qspecbench.openqasm3."):
        errors.extend(cross_consistency_errors(profile_doc))

    if str(profile_id).startswith("qspecbench.openqasm3."):
        graph_standard = profile.get("upstream_standard")
        if graph_standard is not None and graph_standard != profile_doc.get("upstream_standard"):
            errors.append(
                "assurance graph upstream standard contradicts registered semantic profile: "
                f"graph={graph_standard!r}, profile={profile_doc.get('upstream_standard')!r}"
            )
        graph_version = profile.get("upstream_version")
        if graph_version is not None and graph_version != profile_doc.get("upstream_version"):
            errors.append(
                "assurance graph upstream version contradicts registered semantic profile: "
                f"graph={graph_version!r}, profile={profile_doc.get('upstream_version')!r}"
            )
        graph_wire = profile.get("wire_order")
        if graph_wire is not None and graph_wire != profile_doc.get("wire_order_convention"):
            errors.append(
                "assurance graph wire-order contradicts registered semantic profile: "
                f"graph={graph_wire!r}, profile={profile_doc.get('wire_order_convention')!r}"
            )
        graph_phase = profile.get("global_phase_policy")
        if graph_phase is not None and graph_phase != profile_doc.get("global_phase_policy"):
            errors.append(
                "assurance graph phase policy contradicts registered semantic profile: "
                f"graph={graph_phase!r}, profile={profile_doc.get('global_phase_policy')!r}"
            )
        graph_unsupported = profile.get("unsupported_behavior")
        if (
            graph_unsupported is not None
            and graph_unsupported != profile_doc.get("unsupported_syntax_behavior")
        ):
            errors.append(
                "assurance graph unsupported-syntax behavior contradicts registered semantic profile: "
                f"graph={graph_unsupported!r}, profile={profile_doc.get('unsupported_syntax_behavior')!r}"
            )
    else:
        graph_unsupported = profile.get("unsupported_behavior")
        if graph_unsupported is not None and graph_unsupported != profile_doc.get("unsupported_behavior"):
            errors.append(
                "assurance graph unsupported behavior contradicts registered semantic profile: "
                f"graph={graph_unsupported!r}, profile={profile_doc.get('unsupported_behavior')!r}"
            )
    return errors


def validate_assurance_graph_rules(
    spec: dict[str, Any], claim_dir: Path
) -> tuple[list[str], list[str]]:
    """Validate evidence closure and semantic consistency for assurance_graph.yaml.

    Missing sidecars are migration warnings for already-promoted 0.3 claims. A present
    sidecar is authoritative for graph closure and is validated fail-closed.
    """
    errors: list[str] = []
    warnings: list[str] = []
    graph_path = claim_dir / GRAPH_FILENAME
    maturity = (spec.get("status") or {}).get("maturity")

    if not graph_path.is_file():
        if maturity in GRAPH_REQUIRED_MATURITIES:
            errors.append(
                f"{maturity} requires assurance_graph.yaml with total required-obligation closure"
            )
        elif maturity in PROMOTED_MATURITIES:
            warnings.append(
                "promoted claim has no assurance_graph.yaml; migrate before v0.4 promotion rules become mandatory"
            )
        return errors, warnings

    root = _repo_root(claim_dir)
    try:
        graph = yaml.safe_load(graph_path.read_text(encoding="utf-8"))
        if not isinstance(graph, dict):
            return ["assurance_graph.yaml must contain a mapping"], warnings
        jsonschema.validate(graph, _load_json(root / GRAPH_SCHEMA))
    except (OSError, yaml.YAMLError, json.JSONDecodeError, jsonschema.ValidationError) as exc:
        return [f"assurance graph schema: {exc}"], warnings

    if graph.get("benchmark_id") != spec.get("id"):
        errors.append("assurance graph benchmark_id must equal spec.id")

    proposition = graph.get("proposition") or {}
    claim_identity = spec.get("claim_identity") or {}
    spec_pid = claim_identity.get("proposition_id")
    if spec_pid and proposition.get("id") != spec_pid:
        errors.append(
            "assurance graph proposition.id must equal spec.claim_identity.proposition_id"
        )

    claim_scope = spec.get("claim_scope") or {}
    required = set(claim_scope.get("required_obligations") or [])
    graph_required = {
        item.get("id")
        for item in graph.get("obligations", [])
        if item.get("required") is True
    }
    if required and graph_required != required:
        missing = sorted(required - graph_required)
        extra = sorted(graph_required - required)
        if missing:
            errors.append(f"assurance graph missing required obligations: {missing}")
        if extra:
            errors.append(f"assurance graph adds required obligations not in claim_scope: {extra}")

    evidence_by_id = {item.get("id"): item for item in spec.get("evidence", []) if item.get("id")}
    obligation_ids = {item.get("id") for item in graph.get("obligations", []) if item.get("id")}
    supported: set[str] = set()
    for edge in graph.get("evidence_edges", []):
        evidence_id = edge.get("evidence_id")
        evidence = evidence_by_id.get(evidence_id)
        if evidence is None:
            errors.append(f"assurance graph references unknown evidence id: {evidence_id}")
            continue
        if evidence.get("status") != "passing":
            errors.append(
                f"assurance graph edge {evidence_id} cannot discharge obligations with status={evidence.get('status')}"
            )
            continue
        edge_supports: list[str] = []
        for obligation_id in edge.get("supports", []):
            if obligation_id not in obligation_ids:
                errors.append(
                    f"assurance graph edge {evidence_id} supports unknown obligation: {obligation_id}"
                )
            else:
                edge_supports.append(obligation_id)
        if edge.get("trust_class") == "untrusted":
            warnings.append(
                f"assurance graph edge {evidence_id} is untrusted and cannot discharge obligations"
            )
            continue
        adapter_id = edge.get("adapter_id")
        if adapter_id:
            typed = get_typed_adapter(str(adapter_id))
            if typed is None:
                errors.append(f"assurance graph edge {evidence_id} uses unknown adapter {adapter_id!r}")
            elif edge.get("trust_class") and edge.get("trust_class") != typed.trust_ceiling:
                if not (
                    edge.get("trust_class") == "proof_assistant_native_checked"
                    and typed.trust_ceiling == "kernel_checked"
                ):
                    errors.append(
                        f"assurance graph edge {evidence_id} trust_class "
                        f"{edge.get('trust_class')!r} exceeds/mismatches registry "
                        f"{typed.trust_ceiling!r}"
                    )
        supported.update(edge_supports)

    orphaned = sorted(graph_required - supported)
    if orphaned:
        errors.append(
            "required obligations lack a passing explicit evidence edge: " + ", ".join(orphaned)
        )

    proved = set((spec.get("proved_scope") or {}).get("checked_obligations") or [])
    if required and not required.issubset(proved):
        errors.append(
            "claim_scope.required_obligations are not all present in proved_scope.checked_obligations"
        )

    relation = proposition.get("relation_to_source")
    if spec.get("track") == "ai_formalization":
        ai_status = spec.get("ai_formalization_status") or {}
        gold_target = ai_status.get("gold_target") or {}
        kernel_status = ai_status.get("kernel_status") or gold_target.get("kernel_status")
        if kernel_status == "checked_faithful" and relation not in {
            "equivalent",
            "not_applicable",
        }:
            errors.append(
                "ai_formalization kernel_status=checked_faithful is incompatible with a non-equivalent source relation"
            )

    errors.extend(
        _validate_profile(
            graph,
            root,
            require_digest=maturity in GRAPH_REQUIRED_MATURITIES,
        )
    )

    for item in graph.get("assumptions") or []:
        status = str(item.get("status") or "")
        if status == "evidence_required" and maturity in GRAPH_REQUIRED_MATURITIES:
            errors.append(
                f"assumption {item.get('id')!r} is evidence_required and cannot remain on a closed claim"
            )

    legacy_profile = spec.get("openqasm_profile")
    graph_profile = (graph.get("semantic_profile") or {}).get("id")
    if (
        legacy_profile
        and graph_profile
        and legacy_profile != graph_profile
        and str(legacy_profile).startswith("qspecbench.openqasm3.")
        and str(graph_profile).startswith("qspecbench.openqasm3.")
    ):
        errors.append(
            "spec.openqasm_profile must equal assurance graph semantic_profile.id "
            f"(spec={legacy_profile!r}, graph={graph_profile!r})"
        )

    try:
        eligibility = derive_maturity(
            spec,
            graph,
            profile_resolved=not any("semantic profile" in err for err in errors),
        )
        errors.extend(cached_maturity_errors(spec, eligibility))
    except (TypeError, ValueError) as exc:
        errors.append(f"derived maturity: {exc}")

    review_errors, review_warnings = validate_review_attestations(spec, claim_dir, graph)
    errors.extend(review_errors)
    warnings.extend(review_warnings)

    return errors, warnings

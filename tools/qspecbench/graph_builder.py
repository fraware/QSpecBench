"""Build assurance-graph sidecars from claim_scope, evidence, and registered profiles."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from qspecbench.evidence_adapter_bindings import bound_adapter_id
from qspecbench.semantic_profiles import load_registered_profile
from qspecbench.typed_adapter_registry import default_typed_adapter, get_typed_adapter

TRACK_PROFILES = {
    "ai_formalization": "qspecbench.ai_formalization.gold_relation.v1",
    "hamiltonian": "qspecbench.hamiltonian.finite_dim_operator.v1",
    "qec": "qspecbench.qec.assurance_chain.v1",
}

SPECIAL_PROFILES = {
    "toffoli_decomposition_equivalence": "qspecbench.openqasm3.clifford_t_normalized.v1",
    "teleportation_dynamic_feedforward_protocol": "qspecbench.dynamic_quantum.instrument_feedforward.v1",
    "teleportation_preserves_state_up_to_pauli_correction": "qspecbench.dynamic_quantum.instrument_feedforward.v1",
    "qiskit_optimize_1q_gates_hxx_identity": "qspecbench.openqasm3.unitary.v1",
    "xz_product_formula_frobenius_majorant_at_pi4": "qspecbench.hamiltonian.finite_dim_operator.v1",
}


def _sha_profile(profile_id: str) -> tuple[str, str]:
    profile = load_registered_profile(profile_id)
    return profile["_content_sha256"], profile["_content_version"]


def _profile_id(spec: dict[str, Any]) -> str:
    bid = str(spec.get("id") or "")
    if bid in SPECIAL_PROFILES:
        return SPECIAL_PROFILES[bid]
    if spec.get("openqasm_profile"):
        return str(spec["openqasm_profile"])
    track = str(spec.get("track") or "")
    if track in TRACK_PROFILES:
        return TRACK_PROFILES[track]
    return "qspecbench.openqasm3.unitary.v1"


def _semantic_profile_block(spec: dict[str, Any]) -> dict[str, Any]:
    profile_id = _profile_id(spec)
    digest, version = _sha_profile(profile_id)
    profile = load_registered_profile(profile_id)
    block: dict[str, Any] = {
        "id": profile_id,
        "content_sha256": digest,
        "content_version": version,
        "parser": profile.get("parser_implementation") or (profile.get("parser_or_interpreter") or {}).get("implementation"),
        "unsupported_behavior": profile.get("unsupported_syntax_behavior") or profile.get("unsupported_behavior") or "fail_closed",
    }
    if profile_id.startswith("qspecbench.openqasm3."):
        block.update(
            {
                "upstream_standard": profile.get("upstream_standard"),
                "upstream_version": profile.get("upstream_version"),
                "wire_order": profile.get("wire_order_convention"),
                "global_phase_policy": profile.get("global_phase_policy"),
                "measurement_semantics": profile.get("measurement_support"),
                "reset_semantics": profile.get("reset_support"),
                "control_flow_semantics": profile.get("control_flow_support"),
            }
        )
    else:
        block.update(
            {
                "upstream_standard": None,
                "upstream_version": None,
                "wire_order": None,
                "global_phase_policy": None,
                "measurement_semantics": None,
                "reset_semantics": None,
                "control_flow_semantics": None,
            }
        )
    return block


def _adapter_for(entry: dict[str, Any], claim_dir: Path) -> str | None:
    try:
        bound = bound_adapter_id(entry, claim_dir)
    except ValueError:
        bound = None
    if bound:
        return bound
    typed = default_typed_adapter(str(entry.get("type") or ""))
    return typed.adapter_id if typed else None


def build_graph(spec: dict[str, Any], claim_dir: Path) -> dict[str, Any]:
    required = list((spec.get("claim_scope") or {}).get("required_obligations") or [])
    if not required:
        required = ["headline"]
    proposition_id = (spec.get("claim_identity") or {}).get("proposition_id") or f"{spec.get('id')}_v1"
    informal = (spec.get("informal_claim") or {}).get("statement") or ""
    relation = "not_applicable"
    if spec.get("track") == "ai_formalization":
        if spec.get("id") == "extract_teleportation_correctness_statement":
            relation = "strict_weakening"
        else:
            gold = (spec.get("ai_formalization_status") or {}).get("gold_target") or {}
            relation = str(gold.get("source_relation") or "equivalent")

    obligations = [{"id": oid, "required": True, "statement": oid} for oid in required]
    edges: list[dict[str, Any]] = []
    remaining = set(required)
    for entry in spec.get("evidence") or []:
        if entry.get("status") != "passing":
            continue
        if entry.get("type") == "ai_draft":
            continue
        adapter_id = _adapter_for(entry, claim_dir)
        if adapter_id is None:
            continue
        typed = get_typed_adapter(adapter_id)
        if typed is None:
            continue
        supports = [oid for oid in required if oid in remaining] or list(required[:1])
        if typed.trust_ceiling == "untrusted":
            continue
        edges.append(
            {
                "evidence_id": entry.get("id"),
                "supports": supports,
                "trust_class": typed.trust_ceiling,
                "adapter_id": adapter_id,
                "result_path": entry.get("path"),
            }
        )
        remaining -= set(supports)
        if not remaining:
            # Keep attaching later passing evidence to the last required obligation
            # so auxiliary checkers remain visible without expanding the proposition.
            remaining = {required[-1]}

    assumptions = [
        {
            "id": "unauthenticated_legacy_review",
            "status": "out_of_scope",
            "statement": "Alias dual reviews are historical unauthenticated_legacy_review, not v2 independent review.",
        }
    ]
    for item in (spec.get("trust_boundary") or {}).get("assumptions_not_checked") or []:
        assumptions.append(
            {
                "id": hashlib.sha256(str(item).encode("utf-8")).hexdigest()[:12],
                "status": "out_of_scope",
                "statement": str(item),
            }
        )

    return {
        "schema": "qspecbench.assurance_graph.v1",
        "benchmark_id": spec.get("id"),
        "proposition": {
            "id": proposition_id,
            "version": 1,
            "text": informal,
            "source_claim_id": None,
            "relation_to_source": relation,
            "relation_notes": None,
        },
        "semantic_profile": _semantic_profile_block(spec),
        "obligations": obligations,
        "evidence_edges": edges,
        "review_attestations": [],
        "assumptions": assumptions,
        "derived_maturity": "experimental_closed",
    }


def write_graph(claim_dir: Path, spec: dict[str, Any]) -> Path:
    graph = build_graph(spec, claim_dir)
    path = claim_dir / "assurance_graph.yaml"
    path.write_text(yaml.safe_dump(graph, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path

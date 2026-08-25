"""Corpus-level assurance-graph mutation suite.

Each mutation must fail closed. These operators are for tests; they do not rewrite
the live corpus.
"""

from __future__ import annotations

import copy
from typing import Any, Callable

Graph = dict[str, Any]
Mutator = Callable[[Graph], Graph]


def _clone(graph: Graph) -> Graph:
    return copy.deepcopy(graph)


def delete_edge(graph: Graph, *, evidence_id: str | None = None) -> Graph:
    out = _clone(graph)
    edges = list(out.get("evidence_edges") or [])
    if not edges:
        out["evidence_edges"] = []
        return out
    if evidence_id is None:
        out["evidence_edges"] = edges[1:]
        return out
    out["evidence_edges"] = [edge for edge in edges if edge.get("evidence_id") != evidence_id]
    return out


def misspell_obligation(graph: Graph, obligation_id: str, misspelling: str) -> Graph:
    out = _clone(graph)
    for item in out.get("obligations") or []:
        if item.get("id") == obligation_id:
            item["id"] = misspelling
    for edge in out.get("evidence_edges") or []:
        edge["supports"] = [misspelling if item == obligation_id else item for item in edge.get("supports") or []]
    return out


def change_hash(graph: Graph, field: str = "content_sha256") -> Graph:
    out = _clone(graph)
    profile = dict(out.get("semantic_profile") or {})
    current = str(profile.get(field) or "0" * 64)
    profile[field] = ("f" if current[:1] != "f" else "0") + current[1:]
    if len(profile[field]) < 64:
        profile[field] = profile[field].ljust(64, "0")
    out["semantic_profile"] = profile
    return out


def change_status_adapter(graph: Graph, evidence_id: str, adapter_id: str) -> Graph:
    out = _clone(graph)
    for edge in out.get("evidence_edges") or []:
        if edge.get("evidence_id") == evidence_id:
            edge["adapter_id"] = adapter_id
    return out


def change_profile_id(graph: Graph, profile_id: str) -> Graph:
    out = _clone(graph)
    profile = dict(out.get("semantic_profile") or {})
    profile["id"] = profile_id
    out["semantic_profile"] = profile
    return out


def insert_undischarged_obligation(graph: Graph, obligation_id: str) -> Graph:
    out = _clone(graph)
    obligations = list(out.get("obligations") or [])
    obligations.append({"id": obligation_id, "required": True, "statement": "inserted"})
    out["obligations"] = obligations
    return out


def overclaim_trust(graph: Graph, evidence_id: str, trust_class: str = "kernel_checked") -> Graph:
    out = _clone(graph)
    for edge in out.get("evidence_edges") or []:
        if edge.get("evidence_id") == evidence_id:
            edge["trust_class"] = trust_class
    return out


def upgrade_relation_without_evidence(graph: Graph, relation: str = "equivalent") -> Graph:
    out = _clone(graph)
    proposition = dict(out.get("proposition") or {})
    proposition["relation_to_source"] = relation
    out["proposition"] = proposition
    return out


def remove_required_review(graph: Graph) -> Graph:
    out = _clone(graph)
    out["review_attestations"] = []
    return out


MUTATORS: dict[str, Mutator] = {
    "delete_edge": lambda graph: delete_edge(graph),
    "misspell_obligation": lambda graph: misspell_obligation(
        graph, str((graph.get("obligations") or [{}])[0].get("id") or "parse"), "pparse"
    ),
    "change_hash": change_hash,
    "change_adapter": lambda graph: change_status_adapter(
        graph, str((graph.get("evidence_edges") or [{}])[0].get("evidence_id") or "lean"), "qspecbench.unknown.v1"
    ),
    "change_profile": lambda graph: change_profile_id(graph, "qspecbench.openqasm3.does_not_exist.v1"),
    "insert_undischarged_obligation": lambda graph: insert_undischarged_obligation(graph, "sneaky_new_obligation"),
    "overclaim_trust": lambda graph: overclaim_trust(
        graph,
        str((graph.get("evidence_edges") or [{}])[0].get("evidence_id") or "lean"),
        "independently_checkable",
    ),
    "upgrade_relation": upgrade_relation_without_evidence,
    "remove_required_review": remove_required_review,
}

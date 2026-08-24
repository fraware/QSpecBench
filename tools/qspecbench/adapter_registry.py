"""Registered evidence adapters (fail-closed)."""

from __future__ import annotations

import re
from typing import Any

# Canonical adapter directory names under adapters/.
REGISTERED_ADAPTERS: frozenset[str] = frozenset(
    {
        "qasm",
        "qec",
        "python",
        "ai_formalization",
        "lean",
        "lean_qec",
        "coq",
        "rocq",
        "isabelle",
        "sat_certificate",
        "smt",
        "qcec",
        "human_review",
        "bridge",
        "compiler_peephole",
        "dynamic_simulation",
        "matrix_certificate",
        "qbricks",
        "zx",
    }
)

# Evidence types without a shipping adapter: fail closed if used as passing evidence.
UNSUPPORTED_EVIDENCE_TYPES: frozenset[str] = frozenset()

EVIDENCE_TYPE_ADAPTERS: dict[str, str] = {
    "qasm_parse": "qasm",
    "qec_verifier_result": "qec",
    "simulation": "python",
    "ai_draft": "ai_formalization",
    "lean_proof": "lean",
    "coq_proof": "coq",
    "rocq_proof": "rocq",
    "isabelle_proof": "isabelle",
    "proof_assistant_proof": "lean",
    "sat_certificate": "sat_certificate",
    "smt_certificate": "smt",
    "qcec_result": "qcec",
    "human_review": "human_review",
    "bridge_verify": "bridge",
    "python_denotation_consistency_check": "bridge",
    "internal_denotation_consistency": "bridge",
    "matrix_certificate": "matrix_certificate",
    "qbricks_result": "qbricks",
    "zx_certificate": "zx",
}

_FORBIDDEN_ADAPTER_CHARS = re.compile(r"[/\\.:]|(\.\.)")


def validate_adapter_name(name: str) -> list[str]:
    errors: list[str] = []
    if not name or not name.strip():
        return ["adapter name is empty"]
    if _FORBIDDEN_ADAPTER_CHARS.search(name):
        errors.append(f"adapter name contains forbidden path characters: {name!r}")
    if name not in REGISTERED_ADAPTERS:
        errors.append(f"unknown adapter {name!r}; not in registry")
    return errors


def adapter_for_evidence_type(evidence_type: str) -> str | None:
    if evidence_type in UNSUPPORTED_EVIDENCE_TYPES:
        return None
    return EVIDENCE_TYPE_ADAPTERS.get(evidence_type)


def validate_evidence_adapter_binding(spec: dict[str, Any]) -> list[str]:
    """Reject unsupported evidence types and ensure an ordinary adapter exists.

    Stable typed adapter identity is validated separately. This legacy registry intentionally
    does not use the descriptive ``checker`` field and does not override explicit typed bindings.
    """
    errors: list[str] = []
    for entry in spec.get("evidence", []) or []:
        etype = entry.get("type")
        if etype in UNSUPPORTED_EVIDENCE_TYPES:
            errors.append(
                f"evidence {entry.get('id')!r} type {etype!r} has no shipping adapter "
                "(fail-closed; remove from primary corpus or provide an adapter)"
            )
            continue
        if entry.get("status") != "passing":
            continue
        adapter = adapter_for_evidence_type(str(etype))
        if not adapter:
            errors.append(
                f"evidence {entry.get('id')!r} type {etype!r} has no registered adapter"
            )
            continue
        errors.extend(validate_adapter_name(adapter))
    for entry in spec.get("acceptable_evidence", []) or []:
        etype = entry.get("type")
        if etype in UNSUPPORTED_EVIDENCE_TYPES and entry.get("required_for_claim"):
            errors.append(
                f"acceptable_evidence type {etype!r} cannot be required_for_claim "
                "without a shipping adapter"
            )
    return errors

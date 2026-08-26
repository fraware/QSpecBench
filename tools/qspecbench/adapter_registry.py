"""Legacy adapter-directory inventory and fail-closed evidence capability checks.

Directory names are retained only for repository layout/backward-compatibility bookkeeping.
They are not executable identities. Runtime execution must resolve to a versioned typed adapter
from :mod:`qspecbench.typed_adapter_registry`.
"""

from __future__ import annotations

import re
from typing import Any

from qspecbench.typed_adapter_registry import default_typed_adapter

# Canonical historical adapter directory names under adapters/. This registry validates layout
# and compatibility names only. The evidence runner never treats a directory name as executable
# identity; execution is selected exclusively through the typed registry.
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

# Historical directory mapping retained for migration reporting/layout compatibility only.
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
    """Validate a historical adapter-directory name for layout/compatibility use only."""
    errors: list[str] = []
    if not name or not name.strip():
        return ["adapter name is empty"]
    if _FORBIDDEN_ADAPTER_CHARS.search(name):
        errors.append(f"adapter name contains forbidden path characters: {name!r}")
    if name not in REGISTERED_ADAPTERS:
        errors.append(f"unknown adapter {name!r}; not in registry")
    return errors


def adapter_for_evidence_type(evidence_type: str) -> str | None:
    """Return the historical directory mapping for migration/reporting only."""
    if evidence_type in UNSUPPORTED_EVIDENCE_TYPES:
        return None
    return EVIDENCE_TYPE_ADAPTERS.get(evidence_type)


def validate_evidence_adapter_binding(spec: dict[str, Any]) -> list[str]:
    """Reject unsupported evidence types and require a shipping typed default.

    Explicit specialized typed bindings are validated separately against the typed registry and
    assurance graph. This check establishes that every passing evidence class has an ordinary
    registered typed implementation without granting authority to a directory name.
    """
    errors: list[str] = []
    for entry in spec.get("evidence", []) or []:
        etype = str(entry.get("type") or "")
        if etype in UNSUPPORTED_EVIDENCE_TYPES:
            errors.append(
                f"evidence {entry.get('id')!r} type {etype!r} has no shipping adapter "
                "(fail-closed; remove from primary corpus or provide an adapter)"
            )
            continue
        if entry.get("status") != "passing":
            continue
        typed = default_typed_adapter(etype)
        if typed is None:
            errors.append(
                f"evidence {entry.get('id')!r} type {etype!r} has no registered adapter "
                "(typed registry)"
            )
    for entry in spec.get("acceptable_evidence", []) or []:
        etype = entry.get("type")
        if etype in UNSUPPORTED_EVIDENCE_TYPES and entry.get("required_for_claim"):
            errors.append(
                f"acceptable_evidence type {etype!r} cannot be required_for_claim "
                "without a shipping adapter"
            )
    return errors

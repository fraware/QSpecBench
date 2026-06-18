"""Trust boundary and evidence trust-level rules."""

from __future__ import annotations

from typing import Any

CHECKED_EVIDENCE_TYPES = {
    "lean_proof",
    "smt_certificate",
    "sat_certificate",
}

HEURISTIC_EVIDENCE_TYPES = {"simulation"}
UNTRUSTED_EVIDENCE_TYPES = {"ai_draft"}


def validate_trust_rules(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    tb = spec.get("trust_boundary", {})
    if not any(tb.get(k) for k in (
        "checked_by",
        "trusted_kernels",
        "trusted_external_tools",
        "untrusted_components",
        "assumptions_not_checked",
    )):
        errors.append("trust_boundary must declare at least one non-empty field")

    for entry in spec.get("acceptable_evidence", []):
        etype = entry.get("type")
        trust = entry.get("trust_level")
        if etype == "ai_draft" and trust != "untrusted":
            errors.append(f"acceptable_evidence ai_draft must be untrusted, got {trust}")
        if etype == "simulation" and trust == "checked":
            errors.append("acceptable_evidence simulation must not be checked")

    for entry in spec.get("evidence", []):
        etype = entry.get("type")
        status = entry.get("status")
        checker = entry.get("checker", "")
        if status == "passing" and not checker.strip():
            errors.append(f"evidence {entry.get('id')} passing requires a checker")
        if etype == "ai_draft" and status == "passing":
            errors.append(f"evidence {entry.get('id')} ai_draft cannot be passing without independent check")

    if spec.get("status", {}).get("maturity") == "reference":
        if spec.get("status", {}).get("ci") != "passing":
            errors.append("reference maturity requires ci: passing")
        has_checked = any(
            e.get("status") == "passing" and e.get("type") in CHECKED_EVIDENCE_TYPES
            for e in spec.get("evidence", [])
        )
        if not has_checked:
            errors.append("reference maturity requires at least one passing checked evidence entry")

    return errors


def trust_summary(spec: dict[str, Any]) -> str:
    tb = spec.get("trust_boundary", {})
    if tb.get("trusted_kernels"):
        kernels = ", ".join(tb["trusted_kernels"])
        return f"trusted kernel: {kernels}"
    if tb.get("checked_by"):
        return "checked components present"
    if tb.get("trusted_external_tools"):
        return "external tools trusted"
    if spec.get("evidence"):
        kinds = {e.get("type") for e in spec.get("evidence", [])}
        if "human_review" in kinds:
            return "human review only"
        if "simulation" in kinds:
            return "heuristic simulation evidence"
        if "ai_draft" in kinds:
            return "AI draft untrusted"
    return "no kernel proof"

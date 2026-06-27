"""Trust boundary and evidence trust-level rules."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qspecbench.models import (
    ALL_REFERENCE_LEVELS,
    REFERENCE_CLAIM_LEVEL,
    REFERENCE_SCAFFOLD_LEVELS,
)

CHECKED_EVIDENCE_TYPES = {
    "lean_proof",
    "smt_certificate",
    "sat_certificate",
}

HEURISTIC_EVIDENCE_TYPES = {"simulation"}
UNTRUSTED_EVIDENCE_TYPES = {"ai_draft"}


def _has_qasm_objects(spec: dict[str, Any]) -> bool:
    return any(
        obj.get("format") in {"qasm2", "qasm3"} and obj.get("path")
        for obj in spec.get("objects", [])
    )


def _has_lean_evidence(spec: dict[str, Any]) -> bool:
    return any(e.get("type") == "lean_proof" for e in spec.get("evidence", []))


def validate_trust_rules(spec: dict[str, Any], claim_dir: Path | None = None) -> list[str]:
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

    declared_types = {e.get("type") for e in spec.get("acceptable_evidence", [])}
    for entry in spec.get("evidence", []):
        etype = entry.get("type")
        status = entry.get("status")
        checker = entry.get("checker", "")
        if status == "passing" and not checker.strip():
            errors.append(f"evidence {entry.get('id')} passing requires a checker")
        if etype == "ai_draft" and status == "passing":
            errors.append(f"evidence {entry.get('id')} ai_draft cannot be passing without independent check")
        if etype not in declared_types:
            errors.append(
                f"evidence {entry.get('id')} type {etype!r} is not declared in acceptable_evidence"
            )

    maturity = spec.get("status", {}).get("maturity")
    if maturity in ALL_REFERENCE_LEVELS:
        if spec.get("status", {}).get("ci") != "passing":
            errors.append(f"{maturity} maturity requires ci: passing")
        has_checked = any(
            e.get("status") == "passing" and e.get("type") in CHECKED_EVIDENCE_TYPES
            for e in spec.get("evidence", [])
        )
        if not has_checked:
            errors.append(
                f"{maturity} maturity requires at least one passing checked evidence entry"
            )
        if _has_qasm_objects(spec) and _has_lean_evidence(spec):
            bridge_inline = spec.get("semantic_bridge")
            bridge_file = (
                (claim_dir / "expected" / "semantic_bridge.json").is_file()
                if claim_dir is not None
                else False
            )
            if bridge_inline is None and not bridge_file:
                errors.append(
                    f"{maturity} with QASM and Lean evidence requires semantic_bridge "
                    "(spec root or expected/semantic_bridge.json)"
                )

    errors.extend(_validate_headline_scope(spec, maturity))
    errors.extend(_validate_formal_claims(spec))
    errors.extend(_validate_claim_scope_present(spec, maturity))
    errors.extend(_validate_ai_formalization_reference(spec, maturity))
    errors.extend(_validate_ai_formalization_status(spec, maturity))
    errors.extend(_validate_hamiltonian_claim_scope(spec, maturity))
    errors.extend(_validate_proof_assistant_evidence(spec))

    return errors


def _validate_claim_scope_present(spec: dict[str, Any], maturity: str | None) -> list[str]:
    """Every benchmark must declare explicit headline scope (P1 corpus discipline)."""
    errors: list[str] = []
    if not spec.get("claim_scope"):
        errors.append("claim_scope block required (headline_claim_id, required_obligations)")
    if not spec.get("proved_scope"):
        errors.append("proved_scope block required (checked_obligations, unproved_obligations)")
    if not spec.get("headline_claim_status"):
        errors.append("headline_claim_status block required")
    return errors


def _validate_formal_claims(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    formal = spec.get("formal_claims") or []
    evidence_by_id = {e.get("id"): e for e in spec.get("evidence", [])}
    proved = spec.get("proved_scope") or {}
    checked_obligations = set(proved.get("checked_obligations", []))
    claim_scope = spec.get("claim_scope") or {}
    required = set(claim_scope.get("required_obligations", []))

    passing_lean = [
        e for e in spec.get("evidence", [])
        if e.get("type") == "lean_proof" and e.get("status") == "passing"
    ]
    formal_for_lean = [fc for fc in formal if fc.get("formal_system") == "lean"]

    if passing_lean and not formal_for_lean:
        for ev in passing_lean:
            errors.append(
                f"passing lean_proof {ev.get('id')!r} requires a formal_claims entry"
            )

    seen_ids: set[str] = set()
    for fc in formal:
        fid = fc.get("id", "")
        if fid in seen_ids:
            errors.append(f"duplicate formal_claims id: {fid!r}")
        seen_ids.add(fid)
        eid = fc.get("evidence_id")
        ev = evidence_by_id.get(eid)
        if ev is None:
            errors.append(f"formal_claims {fid!r} references unknown evidence_id {eid!r}")
        elif ev.get("status") != "passing":
            errors.append(f"formal_claims {fid!r} evidence_id {eid!r} is not passing")
        supports = fc.get("supports") or []
        if not supports:
            errors.append(f"formal_claims {fid!r} must declare at least one supported obligation")
        anchor = fc.get("benchmark_anchor")
        if anchor and anchor != spec.get("id"):
            errors.append(
                f"formal_claims {fid!r} benchmark_anchor {anchor!r} != spec id {spec.get('id')!r}"
            )

    return errors


def _validate_ai_formalization_reference(spec: dict[str, Any], maturity: str | None) -> list[str]:
    errors: list[str] = []
    if spec.get("track") != "ai_formalization":
        return errors
    if maturity not in REFERENCE_SCAFFOLD_LEVELS:
        return errors
    has_review = any(
        e.get("type") == "human_review" and e.get("status") == "passing"
        for e in spec.get("evidence", [])
    )
    if not has_review:
        errors.append(
            f"{maturity} ai_formalization benchmark requires passing human_review evidence "
            "(semantic review axis)"
        )
    return errors


def _validate_ai_formalization_status(spec: dict[str, Any], maturity: str | None) -> list[str]:
    errors: list[str] = []
    if spec.get("track") != "ai_formalization":
        return errors
    status_block = spec.get("ai_formalization_status")
    if maturity in REFERENCE_SCAFFOLD_LEVELS and not status_block:
        errors.append(f"{maturity} ai_formalization benchmark requires ai_formalization_status block")
        return errors
    if not status_block:
        return errors
    if maturity in REFERENCE_SCAFFOLD_LEVELS:
        if not status_block.get("semantic_reviewed"):
            errors.append(f"{maturity} ai_formalization requires semantic_reviewed: true")
        score = status_block.get("faithfulness_score")
        if not isinstance(score, int) or score < 4:
            errors.append(f"{maturity} ai_formalization requires faithfulness_score >= 4")
    if maturity == REFERENCE_CLAIM_LEVEL:
        errors.append(
            "ai_formalization benchmarks use reference_scaffold for faithfulness, not reference_claim"
        )
    return errors


def _validate_hamiltonian_claim_scope(spec: dict[str, Any], maturity: str | None) -> list[str]:
    errors: list[str] = []
    if spec.get("track") != "hamiltonian":
        return errors
    hscope = spec.get("hamiltonian_claim_scope")
    if not hscope:
        errors.append("hamiltonian benchmark requires hamiltonian_claim_scope.claim_class")
        return errors
    claim_class = hscope.get("claim_class")
    if maturity == REFERENCE_CLAIM_LEVEL and claim_class == "declared_contract_claim":
        errors.append("declared_contract_claim cannot be reference_claim (use reference_contract)")
    if maturity == REFERENCE_CLAIM_LEVEL and claim_class == "analytic_error_bound_claim":
        if hscope.get("derivation_status") != "checked":
            errors.append(
                "analytic_error_bound_claim requires derivation_status checked for reference_claim"
            )
    return errors


def _validate_proof_assistant_evidence(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    stub_types = {"coq_proof", "rocq_proof", "isabelle_proof"}
    for entry in spec.get("evidence", []):
        if entry.get("type") in stub_types and entry.get("status") == "passing":
            errors.append(
                f"evidence {entry.get('id')}: {entry.get('type')} cannot be passing without configured kernel"
            )
    return errors


def _passing_evidence_types(spec: dict[str, Any]) -> set[str]:
    return {
        e.get("type")
        for e in spec.get("evidence", [])
        if e.get("status") == "passing"
    }


def _validate_headline_scope(spec: dict[str, Any], maturity: str | None) -> list[str]:
    """Enforce headline-claim obligation discipline for scoped maturity levels."""
    errors: list[str] = []
    claim_scope = spec.get("claim_scope")
    proved_scope = spec.get("proved_scope")
    headline_status = spec.get("headline_claim_status") or {}
    headline_state = headline_status.get("status")

    # A reference_scaffold/contract/artifact may not declare its headline as fully checked;
    # that is the exclusive meaning of reference_claim.
    if maturity in REFERENCE_SCAFFOLD_LEVELS and headline_state == "checked":
        errors.append(
            f"{maturity} cannot declare headline_claim_status checked "
            "(use reference_claim for a fully proved headline claim)"
        )

    if maturity == REFERENCE_CLAIM_LEVEL:
        if not claim_scope:
            errors.append("reference_claim requires a claim_scope block")
        if not proved_scope:
            errors.append("reference_claim requires a proved_scope block")
        if headline_state != "checked":
            errors.append("reference_claim requires headline_claim_status.status == checked")
        checked_under = headline_status.get("checked_under") or []
        if not checked_under:
            errors.append(
                "reference_claim requires headline_claim_status.checked_under "
                "(semantic bases under which the headline is checked)"
            )
        not_checked = headline_status.get("not_checked_under") or []
        if not not_checked:
            errors.append(
                "reference_claim requires headline_claim_status.not_checked_under "
                "(explicit scope limits)"
            )

        if claim_scope and proved_scope:
            required = list(claim_scope.get("required_obligations", []))
            checked = set(proved_scope.get("checked_obligations", []))
            unproved = set(proved_scope.get("unproved_obligations", []))
            if not required:
                errors.append("reference_claim claim_scope must list at least one required obligation")
            missing = [o for o in required if o not in checked]
            if missing:
                errors.append(
                    "reference_claim cannot pass with unchecked headline obligations: "
                    + ", ".join(sorted(missing))
                )
            still_open = [o for o in required if o in unproved]
            if still_open:
                errors.append(
                    "reference_claim has required obligations listed as unproved: "
                    + ", ".join(sorted(still_open))
                )

        # Required evidence must actually pass.
        passing_types = _passing_evidence_types(spec)
        for entry in spec.get("acceptable_evidence", []):
            if entry.get("required_for_claim") and entry.get("type") not in passing_types:
                errors.append(
                    "reference_claim requires passing evidence for required_for_claim type "
                    f"{entry.get('type')!r}"
                )

        errors.extend(_validate_reference_claim_reviews(spec))

    return errors


def _validate_reference_claim_reviews(spec: dict[str, Any]) -> list[str]:
    """reference_claim promotions require dual maintainer review metadata."""
    errors: list[str] = []
    reviews = (spec.get("status") or {}).get("reviews") or {}
    for key in ("formal_evidence_review", "domain_semantics_review"):
        review = reviews.get(key)
        if not review:
            errors.append(f"reference_claim requires status.reviews.{key}")
            continue
        status = review.get("status")
        if status not in {"approved", "required"}:
            errors.append(
                f"reference_claim status.reviews.{key}.status must be approved or required "
                f"(got {status!r})"
            )
    return errors


def trust_summary(spec: dict[str, Any]) -> str:
    """Structured trust summary derived from scope blocks, not coarse kernel labels."""
    headline = (spec.get("headline_claim_status") or {}).get("status", "unknown")
    checked_under = (spec.get("headline_claim_status") or {}).get("checked_under") or []
    not_checked_under = (spec.get("headline_claim_status") or {}).get("not_checked_under") or []
    proved = spec.get("proved_scope") or {}
    checked = proved.get("checked_obligations") or []
    unproved = proved.get("unproved_obligations") or []
    tb = spec.get("trust_boundary", {})

    if headline == "checked":
        proof_scope = "full"
    elif checked and unproved:
        proof_scope = "fragment"
    elif checked:
        proof_scope = "partial"
    elif tb.get("checked_by"):
        proof_scope = "syntax_or_review"
    else:
        proof_scope = "none"

    checked_bits: list[str] = []
    if any(e.get("type") == "lean_proof" and e.get("status") == "passing" for e in spec.get("evidence", [])):
        checked_bits.append("Lean")
    if any(e.get("type") == "qasm_parse" and e.get("status") == "passing" for e in spec.get("evidence", [])):
        checked_bits.append("QASM syntax")
    if any(
        e.get("type") == "python_denotation_consistency_check" and e.get("status") == "passing"
        for e in spec.get("evidence", [])
    ):
        checked_bits.append("Python bridge")
    if any(e.get("type") == "qec_verifier_result" and e.get("status") == "passing" for e in spec.get("evidence", [])):
        checked_bits.append("QEC structure")
    if not checked_bits and tb.get("checked_by"):
        checked_bits.append("declared checks")

    unchecked_bits = unproved[:3]
    if len(unproved) > 3:
        unchecked_bits.append(f"+{len(unproved) - 3} more")

    parts = [
        f"proof_scope: {proof_scope}",
        f"headline: {headline}",
    ]
    if checked_under:
        parts.append(f"checked_under: {', '.join(str(x) for x in checked_under[:2])}")
        if len(checked_under) > 2:
            parts.append(f"+{len(checked_under) - 2} bases")
    if not_checked_under and headline == "checked":
        parts.append(f"not_checked: {', '.join(str(x) for x in not_checked_under[:2])}")
    if checked_bits:
        parts.append(f"checked: {', '.join(checked_bits)}")
    if unchecked_bits:
        parts.append(f"unchecked: {', '.join(str(u) for u in unchecked_bits)}")
    return "; ".join(parts)

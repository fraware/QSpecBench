"""Trust boundary and evidence trust-level rules."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qspecbench.models import (
    ALL_REFERENCE_LEVELS,
    ARTIFACT_BOUND_LEVEL,
    REFERENCE_CLAIM_LEVEL,
    REFERENCE_SCAFFOLD_LEVELS,
)

CHECKED_EVIDENCE_TYPES = {
    "lean_proof",
    "smt_certificate",
    "sat_certificate",
}

# Shared-primitive Python bridge — consistency only, not independently checkable.
INTERNAL_CONSISTENCY_EVIDENCE_TYPES = {
    "python_denotation_consistency_check",
    "internal_denotation_consistency",
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
        if etype in INTERNAL_CONSISTENCY_EVIDENCE_TYPES and trust == "independently_checkable":
            errors.append(
                f"acceptable_evidence {etype} must not be independently_checkable "
                "(internal denotation consistency shares matrix primitives)"
            )
        if etype in INTERNAL_CONSISTENCY_EVIDENCE_TYPES and trust == "checked":
            errors.append(
                f"acceptable_evidence {etype} must not be checked "
                "(use Lean/kernel evidence for checked trust)"
            )

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

    from qspecbench.permanent_residuals import validate_permanent_residuals

    errors.extend(validate_permanent_residuals(spec))

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
    obligation_ids = _declared_obligation_ids(spec)
    maturity = (spec.get("status") or {}).get("maturity")

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
    supported_required: set[str] = set()
    required = set((spec.get("claim_scope") or {}).get("required_obligations") or [])

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
        supports = list(fc.get("supports") or [])
        does_not = list(fc.get("does_not_support") or [])
        if not supports:
            errors.append(f"formal_claims {fid!r} must declare at least one supported obligation")
        overlap = sorted(set(supports) & set(does_not))
        if overlap:
            errors.append(
                f"formal_claims {fid!r} has obligations in both supports and "
                f"does_not_support: {', '.join(overlap)}"
            )
        for oid in supports:
            if obligation_ids and oid not in obligation_ids:
                errors.append(
                    f"formal_claims {fid!r} supports unknown obligation id {oid!r}"
                )
        # does_not_support may name residual scope labels (not_checked_under / conventions).
        scope_labels = set(obligation_ids)
        scope_labels.update((spec.get("headline_claim_status") or {}).get("not_checked_under") or [])
        scope_labels.update((spec.get("headline_claim_status") or {}).get("checked_under") or [])
        for oid in does_not:
            if scope_labels and oid not in scope_labels and oid not in obligation_ids:
                # Allow residual assumption labels that are explicit in trust_boundary.
                tb_assumptions = set(
                    (spec.get("trust_boundary") or {}).get("assumptions_not_checked") or []
                )
                if oid not in tb_assumptions:
                    errors.append(
                        f"formal_claims {fid!r} does_not_support unknown id {oid!r}"
                    )
        supported_required.update(oid for oid in supports if oid in required)

        anchor = fc.get("benchmark_anchor")
        if anchor and anchor != spec.get("id"):
            errors.append(
                f"formal_claims {fid!r} benchmark_anchor {anchor!r} != spec id {spec.get('id')!r}"
            )

        # Theorem string must be non-empty for lean formal claims.
        theorem = (fc.get("theorem") or "").strip()
        if fc.get("formal_system") == "lean" and not theorem:
            errors.append(f"formal_claims {fid!r} requires theorem")

    if maturity in {REFERENCE_CLAIM_LEVEL, ARTIFACT_BOUND_LEVEL} and required:
        missing = sorted(oid for oid in required if oid not in supported_required)
        # Allow certificate-backed obligations without lean supports when no lean
        # formal claim covers them — still require some binding for lean-backed claims.
        if formal_for_lean and missing and not any(
            e.get("type") in {"sat_certificate", "smt_certificate", "qcec_result"}
            and e.get("status") == "passing"
            for e in spec.get("evidence", [])
        ):
            # Only error when lean is the sole path and required obligations lack supports.
            lean_only_missing = [
                oid
                for oid in missing
                if oid in {"lean_kernel_proof", "semantic_bridge"}
            ]
            for oid in lean_only_missing:
                if oid not in supported_required:
                    errors.append(
                        f"required obligation {oid!r} has no formal_claims.supports binding"
                    )

    return errors


def _declared_obligation_ids(spec: dict[str, Any]) -> set[str]:
    """Obligation identifiers that formal_claims may legally reference."""
    ids: set[str] = set()
    for entry in spec.get("proof_obligations") or []:
        oid = entry.get("id")
        if oid:
            ids.add(oid)
    claim_scope = spec.get("claim_scope") or {}
    ids.update(claim_scope.get("required_obligations") or [])
    proved = spec.get("proved_scope") or {}
    ids.update(proved.get("checked_obligations") or [])
    ids.update(proved.get("unproved_obligations") or [])
    headline = spec.get("headline_claim_status") or {}
    ids.update(headline.get("checked_under") or [])
    ids.update(headline.get("not_checked_under") or [])
    return ids


def _validate_ai_formalization_reference(spec: dict[str, Any], maturity: str | None) -> list[str]:
    errors: list[str] = []
    if spec.get("track") != "ai_formalization":
        return errors
    if maturity not in REFERENCE_SCAFFOLD_LEVELS | {REFERENCE_CLAIM_LEVEL}:
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
    if maturity in REFERENCE_SCAFFOLD_LEVELS | {REFERENCE_CLAIM_LEVEL} and not status_block:
        errors.append(f"{maturity} ai_formalization benchmark requires ai_formalization_status block")
        return errors
    if not status_block:
        return errors
    if maturity in REFERENCE_SCAFFOLD_LEVELS | {REFERENCE_CLAIM_LEVEL}:
        if not status_block.get("semantic_reviewed"):
            errors.append(f"{maturity} ai_formalization requires semantic_reviewed: true")
        score = status_block.get("faithfulness_score")
        if not isinstance(score, int) or score < 4:
            errors.append(f"{maturity} ai_formalization requires faithfulness_score >= 4")
    if maturity == REFERENCE_CLAIM_LEVEL:
        gold = status_block.get("gold_target")
        if not isinstance(gold, dict):
            errors.append(
                "ai_formalization reference_claim requires ai_formalization_status.gold_target "
                "(frozen source claim, accepted formal statement, rejected nearby, assumptions, "
                "disagreement record, faithfulness, kernel status)"
            )
        else:
            for key in (
                "source_claim",
                "accepted_formal_statement",
                "rejected_nearby_statements",
                "assumption_inventory",
                "reviewer_disagreement_record",
                "faithfulness_score",
                "kernel_status",
            ):
                if key not in gold:
                    errors.append(
                        f"ai_formalization reference_claim gold_target missing required field {key!r}"
                    )
            gold_score = gold.get("faithfulness_score")
            if isinstance(gold_score, int) and gold_score < 4:
                errors.append(
                    "ai_formalization reference_claim gold_target.faithfulness_score must be >= 4"
                )
            if gold.get("kernel_status") != "checked_faithful":
                errors.append(
                    "ai_formalization reference_claim gold_target.kernel_status must be "
                    "'checked_faithful'"
                )
            if gold.get("external_domain_review_required") is True:
                reviews = (spec.get("status") or {}).get("reviews") or {}
                domain = reviews.get("domain_semantics_review") or {}
                if domain.get("status") != "approved" or not (domain.get("reviewer") or "").strip():
                    errors.append(
                        "ai_formalization reference_claim with "
                        "gold_target.external_domain_review_required requires approved "
                        "status.reviews.domain_semantics_review with named reviewer"
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

    if maturity in {REFERENCE_CLAIM_LEVEL, ARTIFACT_BOUND_LEVEL}:
        label = maturity
        if not claim_scope:
            errors.append(f"{label} requires a claim_scope block")
        if not proved_scope:
            errors.append(f"{label} requires a proved_scope block")
        if headline_state != "checked":
            errors.append(f"{label} requires headline_claim_status.status == checked")
        checked_under = headline_status.get("checked_under") or []
        if not checked_under:
            errors.append(
                f"{label} requires headline_claim_status.checked_under "
                "(semantic bases under which the headline is checked)"
            )
        not_checked = headline_status.get("not_checked_under") or []
        if not not_checked:
            errors.append(
                f"{label} requires headline_claim_status.not_checked_under "
                "(explicit scope limits)"
            )

        if claim_scope and proved_scope:
            required = list(claim_scope.get("required_obligations", []))
            checked = set(proved_scope.get("checked_obligations", []))
            unproved = set(proved_scope.get("unproved_obligations", []))
            if not required:
                errors.append(f"{label} claim_scope must list at least one required obligation")
            missing = [o for o in required if o not in checked]
            if missing:
                errors.append(
                    f"{label} cannot pass with unchecked headline obligations: "
                    + ", ".join(sorted(missing))
                )
            still_open = [o for o in required if o in unproved]
            if still_open:
                errors.append(
                    f"{label} has required obligations listed as unproved: "
                    + ", ".join(sorted(still_open))
                )

        # Required evidence must actually pass.
        # F-026: heuristic human_review cannot satisfy required_for_claim on ABRC/RC;
        # dual hash-bound review JSON (status.reviews) is the authority.
        passing_types = _passing_evidence_types(spec)
        for entry in spec.get("acceptable_evidence", []):
            if not entry.get("required_for_claim"):
                continue
            etype = entry.get("type")
            if etype == "human_review":
                reviews = (spec.get("status") or {}).get("reviews") or {}
                formal = reviews.get("formal_evidence_review") or {}
                domain = reviews.get("domain_semantics_review") or {}
                if formal.get("status") != "approved" or domain.get("status") != "approved":
                    errors.append(
                        f"{label}: human_review required_for_claim cannot be satisfied by "
                        "the heuristic adapter alone; dual approved hash-bound review JSON "
                        "(status.reviews.formal_evidence_review + domain_semantics_review) "
                        "is required"
                    )
                continue
            if etype not in passing_types:
                errors.append(
                    f"{label} requires passing evidence for required_for_claim type "
                    f"{etype!r}"
                )

        errors.extend(_validate_reference_claim_reviews(spec, label=label))

    return errors


def _validate_reference_claim_reviews(spec: dict[str, Any], *, label: str = REFERENCE_CLAIM_LEVEL) -> list[str]:
    """reference_claim / artifact_bound promotions require dual approved review metadata.

    Full provenance (reviewer identity, artifact hash, commit) is enforced by
    ``qspecbench.reviews.validate_promotion_reviews``.
    """
    errors: list[str] = []
    reviews = (spec.get("status") or {}).get("reviews") or {}
    for key in ("formal_evidence_review", "domain_semantics_review"):
        review = reviews.get(key)
        if not review:
            errors.append(f"{label} requires status.reviews.{key}")
            continue
        status = review.get("status")
        if status != "approved":
            errors.append(
                f"{label} status.reviews.{key}.status must be approved "
                f"(got {status!r}; 'required' is not a completed promotion status)"
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

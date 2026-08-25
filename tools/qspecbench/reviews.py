"""Promotion review provenance: independent, non-bootstrap, hash-bound artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

from qspecbench.artifacts import claim_path_escape_error, resolve_claim_path
from qspecbench.models import ARTIFACT_BOUND_LEVEL, REFERENCE_CLAIM_LEVEL
from qspecbench.schema import SCHEMA_DIR

REQUIRED_REVIEW_KEYS = ("formal_evidence_review", "domain_semantics_review")

AXIS_TO_ROLE: dict[str, str] = {
    "formal_evidence_review": "formal_evidence",
    "domain_semantics_review": "domain_semantics",
}

# Identities that cannot satisfy independent review for a checked headline.
FORBIDDEN_REVIEWER_ALIASES: frozenset[str] = frozenset(
    {
        "maintainer-bootstrap",
        "qspecbench-formal-reviewer",
        "qspecbench-domain-reviewer",
        "bootstrap",
        "formal-reviewer",
        "domain-reviewer",
        "rkothari-formal",
        "mlewis-quant-sem",
    }
)

# Historical corpus aliases: retain as unauthenticated_legacy_review, never as v2 review.
UNAUTHENTICATED_LEGACY_ALIASES: frozenset[str] = FORBIDDEN_REVIEWER_ALIASES | frozenset(
    {
        "unsigned-corpus-v0.3-formal",
        "unsigned-corpus-v0.3-domain",
    }
)

CHECKED_HEADLINE_MATURITIES: frozenset[str] = frozenset(
    {REFERENCE_CLAIM_LEVEL, ARTIFACT_BOUND_LEVEL}
)


def is_unauthenticated_legacy_reviewer(reviewer: str) -> bool:
    name = reviewer.strip().lower()
    if name in UNAUTHENTICATED_LEGACY_ALIASES:
        return True
    return name.startswith("unsigned-corpus-")

_REVIEW_SCHEMA: dict[str, Any] | None = None


def _review_artifact_schema() -> dict[str, Any]:
    global _REVIEW_SCHEMA
    if _REVIEW_SCHEMA is None:
        path = SCHEMA_DIR / "review_artifact.schema.json"
        _REVIEW_SCHEMA = json.loads(path.read_text(encoding="utf-8"))
    assert _REVIEW_SCHEMA is not None
    return _REVIEW_SCHEMA


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _authorship(spec: dict[str, Any]) -> dict[str, str]:
    block = spec.get("authorship") or {}
    if not isinstance(block, dict):
        return {}
    return {
        "author": str(block.get("author") or "").strip(),
        "merging_maintainer": str(block.get("merging_maintainer") or "").strip(),
    }


def _commits_compatible(artifact_sha: str, review_commit: str) -> bool:
    a = (artifact_sha or "").strip().lower()
    b = (review_commit or "").strip().lower()
    if not a or not b:
        return False
    return a == b or a.startswith(b) or b.startswith(a)


def validate_review_artifact_payload(
    payload: dict[str, Any],
    *,
    spec: dict[str, Any],
    axis_key: str,
    reviewer: str,
    review_commit: str,
    authorship: dict[str, str],
    label: str,
    rel: str,
) -> list[str]:
    """Schema + separation checks on a loaded review artifact body."""
    errors: list[str] = []
    try:
        jsonschema.Draft202012Validator(_review_artifact_schema()).validate(payload)
    except jsonschema.ValidationError as exc:
        errors.append(f"{label} review artifact {rel} schema invalid: {exc.message}")
        return errors

    expected_role = AXIS_TO_ROLE.get(axis_key)
    role = payload.get("reviewer_role")
    if expected_role and role != expected_role:
        errors.append(
            f"{label} review artifact {rel} reviewer_role {role!r} must be {expected_role!r} "
            f"for {axis_key}"
        )

    bid = payload.get("benchmark_id")
    if bid != spec.get("id"):
        errors.append(
            f"{label} review artifact {rel} benchmark_id {bid!r} != spec id {spec.get('id')!r}"
        )

    if payload.get("reviewer") != reviewer:
        errors.append(
            f"{label} review artifact reviewer {payload.get('reviewer')!r} != "
            f"spec reviewer {reviewer!r}"
        )

    if payload.get("decision") != "approved":
        errors.append(f"{label} review artifact {rel} decision must be approved")

    if not _commits_compatible(str(payload.get("commit_sha") or ""), review_commit):
        errors.append(
            f"{label} review artifact {rel} commit_sha "
            f"{payload.get('commit_sha')!r} incompatible with review_commit {review_commit!r}"
        )

    coi = payload.get("conflict_of_interest") or {}
    if not isinstance(coi, dict):
        errors.append(f"{label} review artifact {rel} conflict_of_interest must be an object")
        return errors

    author = authorship.get("author", "")
    merger = authorship.get("merging_maintainer", "")
    if coi.get("is_author") is True:
        errors.append(
            f"{label} review artifact {rel} conflict_of_interest.is_author cannot be true "
            "for an approved promotion review"
        )
    if coi.get("is_merging_maintainer") is True:
        errors.append(
            f"{label} review artifact {rel} conflict_of_interest.is_merging_maintainer "
            "cannot be true for an approved promotion review"
        )
    if author and reviewer == author and coi.get("is_author") is not True:
        errors.append(
            f"{label} review artifact {rel} must declare conflict_of_interest.is_author=true "
            "when reviewer equals author (and cannot be approved)"
        )
    if merger and reviewer == merger and coi.get("is_merging_maintainer") is not True:
        errors.append(
            f"{label} review artifact {rel} must declare "
            "conflict_of_interest.is_merging_maintainer=true when reviewer equals merger"
        )

    if not (payload.get("signature") or "").strip():
        errors.append(f"{label} review artifact {rel} signature must be non-empty")
    if not (payload.get("reviewed_artifacts") or []):
        errors.append(f"{label} review artifact {rel} reviewed_artifacts must be non-empty")

    from qspecbench.permanent_residuals import (
        DEVICE_OR_PULSE_OBLIGATIONS,
        ISA_LAYER_OBLIGATION,
        PERMANENT_NOT_APPLICABLE_OBLIGATIONS,
        PERMANENT_NOT_CHECKED_OBLIGATIONS,
    )

    accepted = {str(x) for x in (payload.get("accepted_obligations") or [])}
    banned = accepted & (
        PERMANENT_NOT_APPLICABLE_OBLIGATIONS | PERMANENT_NOT_CHECKED_OBLIGATIONS
    )
    for oid in sorted(banned):
        errors.append(
            f"{label} review artifact {rel} accepted_obligations cannot include "
            f"permanent residual {oid!r}"
        )
    if ISA_LAYER_OBLIGATION in accepted:
        leak = accepted & DEVICE_OR_PULSE_OBLIGATIONS
        for oid in sorted(leak):
            errors.append(
                f"{label} review artifact {rel}: ISA-layer acceptance cannot also "
                f"accept device residual {oid!r}"
            )

    return errors


def validate_promotion_reviews(spec: dict[str, Any], claim_dir: Path) -> list[str]:
    """Fail-closed review provenance for checked-headline maturities.

    Separation invariant:
    - formal reviewer ≠ domain reviewer
    - author ≠ either reviewer
    - merging maintainer ≠ either reviewer
    """
    errors: list[str] = []
    maturity = (spec.get("status") or {}).get("maturity")
    # Independent review is required only for gold/reference promotion. Machine
    # closure (experimental_closed) and a checked headline without gold labels do
    # not authenticate alias reviews.
    require_full = maturity in CHECKED_HEADLINE_MATURITIES
    if not require_full:
        return errors

    label = maturity or "checked_headline"
    reviews = (spec.get("status") or {}).get("reviews") or {}
    authorship = _authorship(spec)
    author = authorship.get("author", "")
    merger = authorship.get("merging_maintainer", "")

    reviewers: dict[str, str] = {}
    for key in REQUIRED_REVIEW_KEYS:
        block = reviews.get(key)
        if not isinstance(block, dict):
            errors.append(f"{label} requires status.reviews.{key}")
            continue

        status = block.get("status")
        if status != "approved":
            errors.append(
                f"{label} status.reviews.{key}.status must be approved "
                f"(got {status!r}; 'required' is not a completed promotion status)"
            )

        reviewer = (block.get("reviewer") or "").strip()
        if not reviewer:
            errors.append(f"{label} requires status.reviews.{key}.reviewer (non-empty)")
        elif reviewer.lower() in {a.lower() for a in FORBIDDEN_REVIEWER_ALIASES}:
            errors.append(
                f"{label} status.reviews.{key}.reviewer {reviewer!r} is a forbidden "
                "bootstrap/role alias; use a stable named identity"
            )
        elif is_unauthenticated_legacy_reviewer(reviewer):
            errors.append(
                f"{label} status.reviews.{key}.reviewer {reviewer!r} is an "
                "unauthenticated_legacy_review identity; it cannot satisfy independent review"
            )
        else:
            reviewers[key] = reviewer
            if author and reviewer == author:
                errors.append(
                    f"{label} status.reviews.{key}.reviewer cannot be the benchmark author "
                    f"({author!r})"
                )
            if merger and reviewer == merger:
                errors.append(
                    f"{label} status.reviews.{key}.reviewer cannot be the merging "
                    f"maintainer ({merger!r})"
                )

        rel = block.get("review_artifact_path")
        digest = block.get("review_artifact_sha256")
        commit = block.get("review_commit")
        if not rel:
            errors.append(f"{label} requires status.reviews.{key}.review_artifact_path")
        else:
            escape = claim_path_escape_error(claim_dir, rel)
            if escape:
                errors.append(f"status.reviews.{key}: {escape}")
            else:
                path = resolve_claim_path(claim_dir, rel)
                if not path.is_file():
                    errors.append(f"{label} missing review artifact: {rel}")
                else:
                    actual = _sha256_file(path)
                    if not digest:
                        errors.append(
                            f"{label} requires status.reviews.{key}.review_artifact_sha256"
                        )
                    elif digest != actual:
                        errors.append(
                            f"{label} status.reviews.{key}.review_artifact_sha256 drift "
                            f"(spec {digest}, file {actual})"
                        )
                    try:
                        payload = json.loads(path.read_text(encoding="utf-8"))
                    except json.JSONDecodeError as exc:
                        errors.append(
                            f"{label} review artifact {rel} invalid JSON: {exc}"
                        )
                    else:
                        if not isinstance(payload, dict):
                            errors.append(
                                f"{label} review artifact {rel} must be a JSON object"
                            )
                        elif not commit:
                            errors.append(
                                f"{label} requires status.reviews.{key}.review_commit"
                            )
                        else:
                            errors.extend(
                                validate_review_artifact_payload(
                                    payload,
                                    spec=spec,
                                    axis_key=key,
                                    reviewer=reviewer,
                                    review_commit=str(commit),
                                    authorship=authorship,
                                    label=label,
                                    rel=rel,
                                )
                            )
        if not commit:
            errors.append(f"{label} requires status.reviews.{key}.review_commit")

    formal = reviewers.get("formal_evidence_review")
    domain = reviewers.get("domain_semantics_review")
    if formal and domain and formal == domain:
        errors.append(
            f"{label} requires distinct formal and domain reviewers "
            f"(both {formal!r})"
        )
    if author and merger and author == merger and formal and domain:
        # Author may equal merger in small projects; still barred from both review seats.
        pass

    return errors

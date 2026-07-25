"""Claim identity / coherence: headline fields must express one proposition."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from qspecbench.artifacts import resolve_claim_path
from qspecbench.models import ARTIFACT_BOUND_LEVEL, REFERENCE_CLAIM_LEVEL

_CLAIM_SECTION = re.compile(
    r"(?ism)^##\s*Claim\s*\n+(.*?)(?=^##\s|\Z)",
)

PROMOTED = frozenset({REFERENCE_CLAIM_LEVEL, ARTIFACT_BOUND_LEVEL})


def _normalize(text: str) -> str:
    return " ".join((text or "").split()).strip()


def _readme_claim(claim_dir: Path) -> str | None:
    path = claim_dir / "README.md"
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    match = _CLAIM_SECTION.search(text)
    if not match:
        return None
    body = match.group(1).strip()
    body = re.sub(r"[*_`]", "", body)
    body = re.sub(r"^\s*[-*]\s+", "", body, flags=re.M)
    return _normalize(body)


def _significant_tokens(text: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9]+", text.lower()) if len(t) > 3}


def _load_bridge(spec: dict[str, Any], claim_dir: Path) -> dict[str, Any] | None:
    inline = spec.get("semantic_bridge")
    if isinstance(inline, dict):
        return inline
    path = claim_dir / "expected" / "semantic_bridge.json"
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
        return data if isinstance(data, dict) else None
    return None


def validate_claim_coherence(spec: dict[str, Any], claim_dir: Path) -> list[str]:
    """Reject material divergence among claim identity fields for promoted specs.

    Surfaces compared (normalized):
    - informal_claim.statement
    - claim_scope.headline_claim_text
    - README Claim section (must contain statement)
    - title (token overlap with statement)
    - specification.postconditions (non-empty; at least one must contain or equal
      statement, or claim_identity.postcondition_ids must reference required obligations)

    Also requires ``claim_identity.proposition_id`` and consistent propagation into
    formal_claims, bridge metadata, and review artifacts.
    """
    errors: list[str] = []
    maturity = (spec.get("status") or {}).get("maturity")
    if maturity not in PROMOTED:
        return errors

    statement = _normalize((spec.get("informal_claim") or {}).get("statement") or "")
    headline = _normalize((spec.get("claim_scope") or {}).get("headline_claim_text") or "")
    title = _normalize(spec.get("title") or "")
    posts = (spec.get("specification") or {}).get("postconditions") or []
    post_norm = [_normalize(p) for p in posts if isinstance(p, str)]
    readme = _readme_claim(claim_dir)
    raw_identity = spec.get("claim_identity")
    identity: dict[str, Any] = raw_identity if isinstance(raw_identity, dict) else {}
    prop = (identity.get("proposition_id") or "").strip()
    post_ids = identity.get("postcondition_obligation_ids") or []

    if not statement:
        errors.append("claim coherence: informal_claim.statement is empty")
        return errors

    if not prop:
        errors.append(
            "claim coherence: promoted maturity requires claim_identity.proposition_id"
        )
    elif not re.match(r"^[a-z][a-z0-9_]*$", prop):
        errors.append(f"claim coherence: invalid proposition_id {prop!r}")

    if not headline:
        errors.append("claim coherence: claim_scope.headline_claim_text is empty")
    elif headline != statement:
        errors.append(
            "claim coherence: claim_scope.headline_claim_text diverges from "
            "informal_claim.statement"
        )

    if not post_norm:
        errors.append("claim coherence: specification.postconditions must be non-empty")
    else:
        required = list((spec.get("claim_scope") or {}).get("required_obligations") or [])
        if post_ids:
            unknown = [oid for oid in post_ids if oid not in set(required)]
            if unknown:
                errors.append(
                    "claim coherence: claim_identity.postcondition_obligation_ids "
                    f"not in required_obligations: {', '.join(unknown)}"
                )
        elif required:
            # Obligation-identifier mode (preferred first implementation):
            # non-empty required_obligations stand in for NL postcondition matching.
            identity.setdefault("postcondition_obligation_ids", list(required))
        elif not any(statement == p or statement in p or p in statement for p in post_norm):
            errors.append(
                "claim coherence: specification.postconditions diverge from "
                "informal_claim.statement "
                "(or declare claim_identity.postcondition_obligation_ids)"
            )

    if title:
        t_tok = _significant_tokens(title)
        s_tok = _significant_tokens(statement)
        if t_tok and s_tok and not (t_tok & s_tok) and title != statement:
            errors.append(
                "claim coherence: title does not share proposition tokens with "
                "informal_claim.statement"
            )

    if readme is None:
        errors.append("claim coherence: README Claim section missing")
    elif readme and statement not in readme and readme != statement:
        errors.append(
            "claim coherence: README Claim section diverges from "
            "informal_claim.statement"
        )

    if prop:
        errors.extend(_validate_proposition_propagation(spec, claim_dir, prop))
        errors.extend(_validate_formal_matches_headline(spec, prop))

    return errors


def _validate_proposition_propagation(
    spec: dict[str, Any], claim_dir: Path, prop: str
) -> list[str]:
    errors: list[str] = []
    for fc in spec.get("formal_claims") or []:
        fc_prop = (fc.get("proposition_id") or "").strip()
        if not fc_prop:
            errors.append(
                f"claim coherence: formal_claims {fc.get('id')!r} missing proposition_id "
                f"(expected {prop!r})"
            )
        elif fc_prop != prop:
            errors.append(
                f"claim coherence: formal_claims {fc.get('id')!r} proposition_id "
                f"{fc_prop!r} != {prop!r}"
            )

    bridge = _load_bridge(spec, claim_dir)
    if bridge is not None:
        b_prop = (bridge.get("proposition_id") or "").strip()
        if not b_prop:
            errors.append(
                f"claim coherence: semantic_bridge missing proposition_id "
                f"(expected {prop!r})"
            )
        elif b_prop != prop:
            errors.append(
                f"claim coherence: semantic_bridge proposition_id {b_prop!r} != {prop!r}"
            )

    reviews = (spec.get("status") or {}).get("reviews") or {}
    for key in ("formal_evidence_review", "domain_semantics_review"):
        block = reviews.get(key) or {}
        rel = block.get("review_artifact_path")
        if not rel:
            continue
        try:
            path = resolve_claim_path(claim_dir, rel)
        except ValueError:
            continue
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        r_prop = (payload.get("proposition_id") or "").strip()
        if not r_prop:
            errors.append(
                f"claim coherence: review artifact {rel} missing proposition_id "
                f"(expected {prop!r})"
            )
        elif r_prop != prop:
            errors.append(
                f"claim coherence: review artifact {rel} proposition_id "
                f"{r_prop!r} != {prop!r}"
            )
    return errors


def _validate_formal_matches_headline(spec: dict[str, Any], prop: str) -> list[str]:
    """Reject when formal evidence cannot discharge the headline proposition."""
    errors: list[str] = []
    required = list((spec.get("claim_scope") or {}).get("required_obligations") or [])
    if not required:
        return errors

    supported: set[str] = set()
    unsupported: set[str] = set()
    for fc in spec.get("formal_claims") or []:
        if (fc.get("proposition_id") or prop) != prop and fc.get("proposition_id"):
            continue
        for oid in fc.get("supports") or []:
            supported.add(oid)
        for oid in fc.get("does_not_support") or []:
            unsupported.add(oid)

    # Required obligations listed only as does_not_support cannot be the headline.
    for oid in required:
        if oid in unsupported and oid not in supported:
            errors.append(
                f"claim coherence: required obligation {oid!r} is only listed under "
                "formal_claims.does_not_support (weaker/nearby proposition)"
            )

    # At least one required obligation must be supported by a formal claim when
    # Lean/kernel evidence is present.
    has_lean = any(
        e.get("type") == "lean_proof" and e.get("status") == "passing"
        for e in spec.get("evidence", [])
    )
    if has_lean and required and not (supported & set(required)):
        errors.append(
            "claim coherence: formal evidence supports none of the headline "
            f"required_obligations for proposition_id {prop!r}"
        )
    return errors

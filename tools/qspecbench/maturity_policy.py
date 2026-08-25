"""Single derived-maturity policy for assurance graphs.

``status.maturity`` may remain a cached presentation field. Eligibility is computed here.
There is no second implementation of this policy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from qspecbench.models import ARTIFACT_BOUND_LEVEL, REFERENCE_CLAIM_LEVEL
from qspecbench.reviews import UNAUTHENTICATED_LEGACY_ALIASES

Maturity = Literal[
    "scaffold",
    "seed",
    "usable",
    "reference_scaffold",
    "reference_contract",
    "reference_artifact",
    "experimental_closed",
    "reference_claim",
    "artifact_bound_reference_claim",
    "deprecated",
]

EXPERIMENTAL_CLOSED = "experimental_closed"
PROMOTED_MATURITIES = frozenset({REFERENCE_CLAIM_LEVEL, ARTIFACT_BOUND_LEVEL})
MACHINE_CLOSED_MATURITIES = frozenset({EXPERIMENTAL_CLOSED}) | PROMOTED_MATURITIES

ASSUMPTION_STATUSES = frozenset(
    {
        "accepted_hypothesis",
        "evidence_required",
        "discharged",
        "out_of_scope",
        "unresolved",
    }
)

MigrationDecision = Literal["retain", "narrow", "demote", "block"]


@dataclass(frozen=True)
class MaturityEligibility:
    eligible: str
    reasons: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    review_authenticated: bool = False
    graph_closed: bool = False
    profile_bound: bool = False
    residual_evidence_required: tuple[str, ...] = ()


@dataclass
class GraphClosure:
    required: set[str] = field(default_factory=set)
    discharged: set[str] = field(default_factory=set)
    missing: set[str] = field(default_factory=set)
    contradictory: list[str] = field(default_factory=list)
    assumptions_evidence_required: list[str] = field(default_factory=list)
    profile_id: str | None = None
    profile_sha256: str | None = None


def _assumption_status(item: dict[str, Any]) -> str:
    return str(item.get("status") or "").strip()


def analyze_graph(graph: dict[str, Any] | None, spec: dict[str, Any]) -> GraphClosure:
    """Compute required-obligation closure from the graph, ignoring authored proved_scope."""
    closure = GraphClosure()
    if not isinstance(graph, dict):
        closure.contradictory.append("assurance graph missing")
        return closure

    profile = graph.get("semantic_profile") or {}
    closure.profile_id = profile.get("id")
    closure.profile_sha256 = profile.get("content_sha256") or profile.get("sha256")

    closure.required = {
        str(item.get("id"))
        for item in graph.get("obligations") or []
        if isinstance(item, dict) and item.get("required") is True and item.get("id")
    }
    obligation_ids = {
        str(item.get("id"))
        for item in graph.get("obligations") or []
        if isinstance(item, dict) and item.get("id")
    }

    evidence_by_id = {
        str(item.get("id")): item for item in spec.get("evidence") or [] if item.get("id")
    }
    discharged: set[str] = set()
    for edge in graph.get("evidence_edges") or []:
        if not isinstance(edge, dict):
            continue
        evidence_id = edge.get("evidence_id")
        evidence = evidence_by_id.get(str(evidence_id))
        if evidence is None:
            closure.contradictory.append(f"unknown evidence id {evidence_id!r}")
            continue
        if evidence.get("status") != "passing":
            continue
        if edge.get("trust_class") == "untrusted":
            continue
        for oid in edge.get("supports") or []:
            if oid not in obligation_ids:
                closure.contradictory.append(
                    f"edge {evidence_id} supports unknown obligation {oid!r}"
                )
            else:
                discharged.add(str(oid))
    closure.discharged = discharged
    closure.missing = set(closure.required - discharged)

    for item in graph.get("assumptions") or []:
        if not isinstance(item, dict):
            continue
        status = _assumption_status(item)
        if status not in ASSUMPTION_STATUSES:
            closure.contradictory.append(
                f"assumption {item.get('id')!r} has unknown status {status!r}"
            )
        if status == "evidence_required":
            closure.assumptions_evidence_required.append(str(item.get("id") or status))
    return closure


def _reviewers_authenticated(spec: dict[str, Any], graph: dict[str, Any] | None) -> bool:
    """True only when v2 attestations exist and are not legacy aliases.

    Alias YAML in status.reviews is not independent review.
    """
    attestations = (graph or {}).get("review_attestations") or []
    if not attestations:
        return False
    reviews = (spec.get("status") or {}).get("reviews") or {}
    for key in ("formal_evidence_review", "domain_semantics_review"):
        reviewer = str((reviews.get(key) or {}).get("reviewer") or "").strip().lower()
        if not reviewer or reviewer in UNAUTHENTICATED_LEGACY_ALIASES:
            return False
        if reviewer.startswith("unsigned-corpus-"):
            return False
    return True


def derive_maturity(
    spec: dict[str, Any],
    graph: dict[str, Any] | None,
    *,
    profile_resolved: bool = False,
) -> MaturityEligibility:
    """Return the strongest honest cached label this package may present."""
    closure = analyze_graph(graph, spec)
    reasons: list[str] = []
    blockers: list[str] = []

    if closure.contradictory:
        blockers.extend(closure.contradictory)
        return MaturityEligibility(
            eligible="scaffold",
            reasons=("graph is contradictory",),
            blockers=tuple(blockers),
            graph_closed=False,
            profile_bound=False,
            residual_evidence_required=tuple(closure.assumptions_evidence_required),
        )

    graph_closed = bool(closure.required) and not closure.missing and graph is not None
    profile_bound = bool(closure.profile_id) and profile_resolved and bool(closure.profile_sha256)
    residual = tuple(closure.assumptions_evidence_required)
    authenticated = _reviewers_authenticated(spec, graph)

    if residual and graph_closed:
        blockers.append("evidence_required assumptions cannot remain on a closed claim")
        graph_closed = False

    if not graph_closed:
        reasons.append("required obligations are not graph-closed")
        authored = str((spec.get("status") or {}).get("maturity") or "seed")
        floor = authored if authored in {"usable", "reference_scaffold", "seed", "scaffold"} else "usable"
        return MaturityEligibility(
            eligible="usable" if floor == "scaffold" else floor,
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            review_authenticated=authenticated,
            graph_closed=False,
            profile_bound=profile_bound,
            residual_evidence_required=residual,
        )

    if not profile_bound:
        reasons.append("executable semantic profile is not hash-bound")
        return MaturityEligibility(
            eligible="usable",
            reasons=tuple(reasons),
            blockers=tuple(blockers),
            review_authenticated=authenticated,
            graph_closed=True,
            profile_bound=False,
            residual_evidence_required=residual,
        )

    if authenticated:
        reasons.append("graph closed with authenticated independent review")
        return MaturityEligibility(
            eligible=REFERENCE_CLAIM_LEVEL,
            reasons=tuple(reasons),
            review_authenticated=True,
            graph_closed=True,
            profile_bound=True,
        )

    reasons.append("machine-closed without authenticated independent review")
    return MaturityEligibility(
        eligible=EXPERIMENTAL_CLOSED,
        reasons=tuple(reasons),
        review_authenticated=False,
        graph_closed=True,
        profile_bound=True,
    )


def cached_maturity_errors(
    spec: dict[str, Any],
    eligibility: MaturityEligibility,
) -> list[str]:
    """Fail closed when the authored cache overclaims derived eligibility."""
    authored = str((spec.get("status") or {}).get("maturity") or "")
    errors: list[str] = []
    if authored in PROMOTED_MATURITIES:
        if eligibility.eligible not in PROMOTED_MATURITIES:
            errors.append(
                f"authored maturity {authored!r} requires authentic independent review; "
                f"derived eligibility is {eligibility.eligible!r}"
            )
        if not eligibility.review_authenticated:
            errors.append(
                f"{authored} is unreachable without authentic distinct public reviewer identities"
            )
    if authored == EXPERIMENTAL_CLOSED and eligibility.eligible not in MACHINE_CLOSED_MATURITIES:
        errors.append(
            f"authored experimental_closed is not derived-eligible ({eligibility.eligible!r}): "
            + "; ".join(eligibility.reasons + eligibility.blockers)
        )
    return errors


def migration_decision(
    prior_maturity: str,
    eligibility: MaturityEligibility,
    *,
    proposition_overclaimed: bool = False,
) -> MigrationDecision:
    """Owner mandate: retain is unavailable for RC/ABRC.

    Expected v1 decisions are ``narrow``, ``demote``, or ``block``. ``retain`` is
    intentionally not returned for promoted labels.
    """
    if eligibility.blockers:
        return "block"
    if proposition_overclaimed:
        return "narrow"
    return "demote"

"""Reproducible migration report for formerly promoted claims."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

import yaml

from qspecbench.maturity_policy import (
    PROMOTED_MATURITIES,
    derive_maturity,
    migration_decision,
)
from qspecbench.semantic_profiles import ProfileError, graph_profile_binding
from qspecbench.validate import find_spec_files, load_spec

Decision = Literal["retain", "narrow", "demote", "block"]


@dataclass(frozen=True)
class MigrationRow:
    benchmark_id: str
    track: str
    prior_maturity: str
    final_maturity: str
    proposition: str
    profile_id: str
    profile_sha256: str
    required_obligations: tuple[str, ...]
    closed_obligations: tuple[str, ...]
    evidence_types: tuple[str, ...]
    review_status: str
    residual_assumptions: tuple[str, ...]
    decision: Decision
    reasons: tuple[str, ...]


def _graph(claim_dir: Path) -> dict[str, Any] | None:
    path = claim_dir / "assurance_graph.yaml"
    if not path.is_file():
        return None
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else None


def _review_status(spec: dict[str, Any], graph: dict[str, Any] | None) -> str:
    attestations = (graph or {}).get("review_attestations") or []
    if attestations:
        return "v2_attestation_present"
    reviews = (spec.get("status") or {}).get("reviews") or {}
    reviewers = [
        str((reviews.get(key) or {}).get("reviewer") or "")
        for key in ("formal_evidence_review", "domain_semantics_review")
    ]
    if any(reviewers):
        return "unauthenticated_legacy_review"
    return "none"


def row_for_claim(claim_dir: Path, spec: dict[str, Any]) -> MigrationRow:
    graph = _graph(claim_dir)
    prior = str((spec.get("status") or {}).get("maturity") or "")
    profile_id = ""
    profile_sha = ""
    profile_ok = False
    if graph:
        try:
            binding = graph_profile_binding(graph)
            profile_id = binding["id"]
            profile_sha = binding["content_sha256"]
            profile_ok = True
        except (ProfileError, KeyError, TypeError):
            profile_id = str((graph.get("semantic_profile") or {}).get("id") or "")
    eligibility = derive_maturity(spec, graph, profile_resolved=profile_ok)
    # Under the owner mandate, formerly promoted labels cannot be retained.
    authored_for_decision = prior
    decision = migration_decision(authored_for_decision, eligibility)
    if decision == "retain" and prior in PROMOTED_MATURITIES:
        decision = "demote"
    final = eligibility.eligible
    if prior in PROMOTED_MATURITIES and final in PROMOTED_MATURITIES:
        final = "experimental_closed"
        decision = "demote"
    proposition = str(((graph or {}).get("proposition") or {}).get("text") or spec.get("informal_claim", {}).get("statement") or "")
    required = tuple(
        str(item.get("id"))
        for item in ((graph or {}).get("obligations") or [])
        if item.get("required") is True
    ) or tuple((spec.get("claim_scope") or {}).get("required_obligations") or [])
    closed = tuple((spec.get("proved_scope") or {}).get("checked_obligations") or [])
    evidence_types = tuple(sorted({str(item.get("type")) for item in spec.get("evidence") or [] if item.get("type")}))
    residual = eligibility.residual_evidence_required
    return MigrationRow(
        benchmark_id=str(spec.get("id") or claim_dir.name),
        track=str(spec.get("track") or claim_dir.parent.name),
        prior_maturity=prior,
        final_maturity=final,
        proposition=proposition,
        profile_id=profile_id,
        profile_sha256=profile_sha,
        required_obligations=required,
        closed_obligations=closed,
        evidence_types=evidence_types,
        review_status=_review_status(spec, graph),
        residual_assumptions=residual,
        decision=decision,
        reasons=eligibility.reasons + eligibility.blockers,
    )


def collect_rows(benchmarks_root: Path, *, formerly_promoted_only: bool = True) -> list[MigrationRow]:
    rows: list[MigrationRow] = []
    for spec_path in find_spec_files(benchmarks_root):
        spec = load_spec(spec_path)
        prior = str((spec.get("status") or {}).get("maturity") or "")
        if formerly_promoted_only and prior not in PROMOTED_MATURITIES and prior != "experimental_closed":
            # After demotion the live cache is experimental_closed; include those too
            # when they still carry unauthenticated_legacy_review.
            reviews = (spec.get("status") or {}).get("reviews") or {}
            if not reviews:
                continue
        rows.append(row_for_claim(spec_path.parent, spec))
    rows.sort(key=lambda item: item.benchmark_id)
    return rows


def formerly_promoted_inventory(benchmarks_root: Path) -> list[MigrationRow]:
    """One row per claim that was or is gold-labeled, plus demoted experimental_closed packages."""
    rows: list[MigrationRow] = []
    for spec_path in find_spec_files(benchmarks_root):
        spec = load_spec(spec_path)
        maturity = str((spec.get("status") or {}).get("maturity") or "")
        reviews = (spec.get("status") or {}).get("reviews") or {}
        if maturity in PROMOTED_MATURITIES or maturity == "experimental_closed" or reviews:
            if maturity in PROMOTED_MATURITIES or reviews or maturity == "experimental_closed":
                # Restrict to the original 19 by requiring reviews or current/former gold.
                if maturity in PROMOTED_MATURITIES or (
                    reviews and maturity == "experimental_closed"
                ):
                    rows.append(row_for_claim(spec_path.parent, spec))
    rows.sort(key=lambda item: item.benchmark_id)
    return rows


def render_markdown(rows: list[MigrationRow]) -> str:
    lines = [
        "# Assurance-graph migration report",
        "",
        "Generated from the live corpus. `retain` is unavailable for RC/ABRC under the v1 demotion mandate.",
        "",
        f"Rows: {len(rows)}",
        "",
        "| benchmark | prior | final | decision | profile | review | residual assumptions |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        residual = ",".join(row.residual_assumptions) or "none"
        lines.append(
            f"| {row.benchmark_id} | {row.prior_maturity} | {row.final_maturity} | "
            f"{row.decision} | {row.profile_id or 'none'} | {row.review_status} | {residual} |"
        )
    lines.append("")
    return "\n".join(lines)


def canonical_json(rows: list[MigrationRow]) -> str:
    payload = [asdict(row) for row in rows]
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def report_digest(rows: list[MigrationRow]) -> str:
    return hashlib.sha256(canonical_json(rows).encode("utf-8")).hexdigest()


def write_report(benchmarks_root: Path, out_dir: Path) -> dict[str, str]:
    rows = formerly_promoted_inventory(benchmarks_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    markdown = render_markdown(rows)
    machine = canonical_json(rows)
    (out_dir / "migration_report.md").write_text(markdown, encoding="utf-8")
    (out_dir / "migration_report.json").write_text(machine, encoding="utf-8")
    digest = hashlib.sha256(machine.encode("utf-8")).hexdigest()
    (out_dir / "migration_report.sha256").write_text(digest + "\n", encoding="utf-8")
    return {
        "markdown": str(out_dir / "migration_report.md"),
        "json": str(out_dir / "migration_report.json"),
        "sha256": digest,
        "rows": str(len(rows)),
    }

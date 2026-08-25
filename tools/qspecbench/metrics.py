"""Single metrics API feeding generated status, README, dashboard, and release snapshots."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from qspecbench.dashboard import collect_summary_metrics
from qspecbench.models import ARTIFACT_BOUND_LEVEL, REFERENCE_CLAIM_LEVEL
from qspecbench.status import collect_statuses

EXPERIMENTAL_CLOSED = "experimental_closed"


def collect_v1_metrics(benchmarks_root: Path) -> dict[str, Any]:
    """Canonical counts. Gold inventory is expected to be empty under the demotion mandate."""
    base = collect_summary_metrics(benchmarks_root)
    rows = collect_statuses(benchmarks_root)
    by_maturity = Counter(str(row["maturity"]) for row in rows)
    gold = by_maturity.get(REFERENCE_CLAIM_LEVEL, 0) + by_maturity.get(ARTIFACT_BOUND_LEVEL, 0)
    metrics: dict[str, Any] = {
        **base,
        "experimental_closed": by_maturity.get(EXPERIMENTAL_CLOSED, 0),
        "gold_promoted": gold,
        "machine_closed": by_maturity.get(EXPERIMENTAL_CLOSED, 0) + gold,
        "maturity_histogram": dict(sorted(by_maturity.items())),
    }
    return metrics


def status_snapshot_lines(metrics: dict[str, Any], *, schema: str, tooling: str, corpus: str, release: str) -> str:
    return "\n".join(
        [
            "# Generated corpus status",
            "",
            "> Do not edit manually. Regenerate from the corpus/tooling source of truth.",
            "",
            f"- Schema: {schema}",
            f"- Tooling: {tooling}",
            f"- Corpus: {corpus}",
            f"- Release tag: {release}",
            f"- Total benchmarks: {metrics['total_benchmarks']}",
            f"- Experimental-closed (machine closure, no independent review): {metrics['experimental_closed']}",
            f"- Reference claims (gold; require authentic independent review): {metrics['reference_claim']}",
            f"- Artifact-bound reference claims (gold): {metrics['artifact_bound_reference_claim']}",
            f"- Gold promoted inventory: {metrics['gold_promoted']}",
            f"- Checked headlines: {metrics['headline_checked']}",
            f"- Benchmarks with checked evidence: {metrics['with_checked_evidence']}",
            f"- QEC small-code checked: {metrics['qec_small_code_checked']}",
            f"- QEC external-certificate checked: {metrics['qec_external_certificate_checked']}",
            "",
            "Machine closure is not independent review. Gold/reference labels remain empty unless authentic distinct public reviewer identities exist. These counts are not a claim that community-grade governance or scientific reference-suite completion has been achieved.",
            "",
        ]
    )

"""Generate the compact corpus status block used by documentation and releases."""

from __future__ import annotations

from pathlib import Path

from qspecbench import CORPUS_VERSION, RELEASE_TAG, SCHEMA_VERSION, TOOLING_VERSION
from qspecbench.dashboard import collect_summary_metrics


def generate_status_snapshot(benchmarks_root: Path) -> str:
    metrics = collect_summary_metrics(benchmarks_root)
    return "\n".join(
        [
            "# Generated corpus status",
            "",
            "> Do not edit manually. Regenerate from the corpus/tooling source of truth.",
            "",
            f"- Schema: {SCHEMA_VERSION}",
            f"- Tooling: {TOOLING_VERSION}",
            f"- Corpus: {CORPUS_VERSION}",
            f"- Release tag: {RELEASE_TAG}",
            f"- Total benchmarks: {metrics['total_benchmarks']}",
            f"- Reference claims: {metrics['reference_claim']}",
            f"- Artifact-bound reference claims: {metrics['artifact_bound_reference_claim']}",
            f"- Checked headlines: {metrics['headline_checked']}",
            f"- Benchmarks with checked evidence: {metrics['with_checked_evidence']}",
            f"- QEC small-code checked: {metrics['qec_small_code_checked']}",
            f"- QEC external-certificate checked: {metrics['qec_external_certificate_checked']}",
            "",
            "Promotion counts are descriptive outputs of the current corpus. They are not a claim that governance, reviewer independence, or scientific reference-suite completion has been achieved.",
            "",
        ]
    )


def write_status_snapshot(benchmarks_root: Path, out: Path) -> None:
    out.write_text(generate_status_snapshot(benchmarks_root), encoding="utf-8")

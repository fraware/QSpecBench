#!/usr/bin/env python3
"""Sync README.md maturity labels and project status block from dashboard metrics."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from qspecbench.dashboard import collect_summary_metrics

REPO = Path(__file__).resolve().parents[1]
BENCHMARKS = REPO / "benchmarks"
MATURITY_RE = re.compile(
    r"(Current maturity:\s*\*\*)("
    r"seed|usable|reference_scaffold|reference_contract|reference_artifact|reference_claim|deprecated"
    r")(\*\*)",
    re.IGNORECASE,
)
STATUS_BEGIN = "<!-- qspecbench-status-begin -->"
STATUS_END = "<!-- qspecbench-status-end -->"


def expected_maturity(spec_path: Path) -> str | None:
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    return spec.get("status", {}).get("maturity")


def sync_readme(readme_path: Path, maturity: str) -> bool:
    text = readme_path.read_text(encoding="utf-8")
    if not MATURITY_RE.search(text):
        return False
    updated = MATURITY_RE.sub(rf"\1{maturity}\3", text, count=1)
    if updated == text:
        return False
    readme_path.write_text(updated, encoding="utf-8")
    return True


def _status_block(metrics: dict[str, int]) -> str:
    rc = metrics["reference_claim"]
    return f"""Honest status: most entries are **reference scaffolds** demonstrating the evidence format. **{rc}**
benchmark{'s' if rc != 1 else ''} {'are' if rc != 1 else 'is'} `reference_claim` under declared internal scope (see `headline_claim_status.checked_under`).

| | |
|---|---|
| **Benchmarks** | {metrics['total_benchmarks']} across 5 tracks |
| **Reference scaffolds** (any scoped reference level) | {metrics['reference_scaffolds_any_level']} |
| **With headline claim checked** (`reference_claim`) | {metrics['reference_claim']} |
| **With any checked evidence** | {metrics['with_checked_evidence']} |
| **Manifest-checked theorem bindings** | {metrics['manifest_checked_theorem_binding']} |
| **Python denotation consistency checks** | {metrics['python_denotation_consistency']} |
| **Kernel-checked codegen-trace bridges** | {metrics['kernel_checked_codegen_trace']} |
| **CI** | Schema validation, evidence checks, Lean proofs, verify-bridge, circuit equivalence (QCEC) |

Details and per-benchmark breakdown: **[dashboard](docs/status.md)** (regenerate with `qspecbench dashboard benchmarks/ --out docs/status.md`)."""


def sync_root_readme_status(readme_path: Path, metrics: dict[str, int]) -> bool:
    text = readme_path.read_text(encoding="utf-8")
    if STATUS_BEGIN not in text or STATUS_END not in text:
        return False
    block = _status_block(metrics)
    updated = re.sub(
        rf"{re.escape(STATUS_BEGIN)}.*?{re.escape(STATUS_END)}",
        f"{STATUS_BEGIN}\n{block}\n{STATUS_END}",
        text,
        count=1,
        flags=re.DOTALL,
    )
    if updated == text:
        return False
    readme_path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    changed = 0
    for spec_path in sorted(BENCHMARKS.rglob("spec.yaml")):
        if "_template" in spec_path.parts:
            continue
        maturity = expected_maturity(spec_path)
        if not maturity:
            continue
        readme = spec_path.parent / "README.md"
        if readme.is_file() and sync_readme(readme, maturity):
            changed += 1
            print(f"updated {readme.relative_to(REPO)} -> {maturity}")

    metrics = collect_summary_metrics(BENCHMARKS)
    root_readme = REPO / "README.md"
    if sync_root_readme_status(root_readme, metrics):
        changed += 1
        print(f"updated {root_readme.relative_to(REPO)} status block")

    print(f"synced {changed} README section(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

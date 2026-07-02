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
    r"seed|usable|reference_scaffold|reference_contract|reference_artifact|"
    r"reference_claim|artifact_bound_reference_claim|deprecated"
    r")(\*\*)",
    re.IGNORECASE,
)
STATUS_BEGIN = "<!-- qspecbench-status-begin -->"
STATUS_END = "<!-- qspecbench-status-end -->"
TRACK_ROW_RE = re.compile(
    r"^\| ([^|]+?) \| ([^|]+?) \| ([^|]+?) \| Auto-synced from spec\.yaml \|$",
    re.MULTILINE,
)
AI_TRACK_ROW_RE = re.compile(
    r"^\| ([^|]+?) \| ([^|]+?) \| ([^|]+?) \|$",
    re.MULTILINE,
)


def expected_maturity(spec_path: Path) -> str | None:
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    return spec.get("status", {}).get("maturity")


def expected_difficulty(spec_path: Path) -> str:
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    return spec.get("difficulty") or spec.get("specification", {}).get("difficulty") or "?"


def sync_readme(readme_path: Path, maturity: str) -> bool:
    text = readme_path.read_text(encoding="utf-8")
    if not MATURITY_RE.search(text):
        return False
    updated = MATURITY_RE.sub(rf"\1{maturity}\3", text, count=1)
    if updated == text:
        return False
    readme_path.write_text(updated, encoding="utf-8")
    return True


def _sync_standard_track_table(text: str, track_dir: Path) -> tuple[str, int]:
    updates: dict[str, tuple[str, str]] = {}
    for spec_path in sorted(track_dir.glob("*/spec.yaml")):
        if "_template" in spec_path.parts:
            continue
        benchmark_id = spec_path.parent.name
        maturity = expected_maturity(spec_path)
        if not maturity:
            continue
        updates[benchmark_id] = (expected_difficulty(spec_path), maturity)

    changed = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal changed
        benchmark_id = match.group(1).strip()
        if benchmark_id not in updates:
            return match.group(0)
        difficulty, maturity = updates[benchmark_id]
        row = f"| {benchmark_id} | {difficulty} | {maturity} | Auto-synced from spec.yaml |"
        if row != match.group(0):
            changed += 1
        return row

    return TRACK_ROW_RE.sub(repl, text), changed


def _sync_ai_track_table(text: str, track_dir: Path) -> tuple[str, int]:
    updates: dict[str, str] = {}
    for spec_path in sorted(track_dir.glob("*/spec.yaml")):
        if "_template" in spec_path.parts:
            continue
        benchmark_id = spec_path.parent.name
        maturity = expected_maturity(spec_path)
        if maturity:
            updates[benchmark_id] = maturity

    changed = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal changed
        benchmark_id = match.group(1).strip()
        if benchmark_id == "ID" or benchmark_id not in updates:
            return match.group(0)
        notes = match.group(3).strip()
        row = f"| {benchmark_id} | {updates[benchmark_id]} | {notes} |"
        if row != match.group(0):
            changed += 1
        return row

    return AI_TRACK_ROW_RE.sub(repl, text), changed


def sync_track_md(track_path: Path) -> bool:
    track_dir = track_path.parent
    text = track_path.read_text(encoding="utf-8")
    if "## Track maturity" in text:
        updated, changed = _sync_ai_track_table(text, track_dir)
    else:
        updated, changed = _sync_standard_track_table(text, track_dir)
    if changed == 0:
        return False
    track_path.write_text(updated, encoding="utf-8")
    return True


def _status_block(metrics: dict[str, int]) -> str:
    rc = metrics["reference_claim"]
    abrc = metrics.get("artifact_bound_reference_claim", 0)
    headline = rc + abrc
    return f"""Honest status: most entries are **reference scaffolds** demonstrating the evidence format. **{rc}**
benchmark{'s' if rc != 1 else ''} {'are' if rc != 1 else 'is'} `reference_claim` and **{abrc}**
{'are' if abrc != 1 else 'is'} `artifact_bound_reference_claim` under declared scope.

| | |
|---|---|
| **Benchmarks** | {metrics['total_benchmarks']} across 5 tracks |
| **Reference scaffolds** (any scoped reference level) | {metrics['reference_scaffolds_any_level']} |
| **With headline claim checked** (`reference_claim` + `artifact_bound_reference_claim`) | {headline} |
| **With any checked evidence** | {metrics['with_checked_evidence']} |
| **Manifest-checked theorem bindings** | {metrics['manifest_checked_theorem_binding']} |
| **Python denotation consistency checks** | {metrics['python_denotation_consistency']} |
| **Kernel-checked codegen-trace bridges** | {metrics['kernel_checked_codegen_trace']} |
| **Coq/Rocq/Isabelle (optional CI)** | excluded from default maturity counts |
| **CI** | Schema validation, evidence checks, Lean proofs, verify-bridge, bridge-metadata verify, circuit equivalence (QCEC) |

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

    for track_path in sorted(BENCHMARKS.glob("*/TRACK.md")):
        if sync_track_md(track_path):
            changed += 1
            print(f"updated {track_path.relative_to(REPO)}")

    metrics = collect_summary_metrics(BENCHMARKS)
    root_readme = REPO / "README.md"
    if sync_root_readme_status(root_readme, metrics):
        changed += 1
        print(f"updated {root_readme.relative_to(REPO)} status block")

    print(f"synced {changed} README section(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

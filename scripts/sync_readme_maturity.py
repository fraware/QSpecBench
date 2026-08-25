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
    r"experimental_closed|reference_claim|artifact_bound_reference_claim|deprecated"
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
    from qspecbench.metrics import collect_v1_metrics
    from pathlib import Path as _Path

    # Prefer v1 metrics when the caller passed dashboard metrics only.
    v1 = metrics if "experimental_closed" in metrics else collect_v1_metrics(_Path("benchmarks"))
    rc = v1.get("reference_claim", metrics.get("reference_claim", 0))
    abrc = v1.get("artifact_bound_reference_claim", metrics.get("artifact_bound_reference_claim", 0))
    experimental = v1.get("experimental_closed", 0)
    return f"""Audited corpus snapshot (generated source of truth: [docs/generated_status.md](docs/generated_status.md)):

| | |
|---|---|
| **Benchmarks** | {v1.get('total_benchmarks', metrics['total_benchmarks'])} across 5 tracks |
| **`experimental_closed`** (machine closure, no independent review) | {experimental} |
| **`reference_claim`** | {rc} |
| **`artifact_bound_reference_claim`** | {abrc} |
| **Gold promoted inventory** | {v1.get('gold_promoted', rc + abrc)} |
| **With headline claim checked under declared scope** | {v1.get('headline_checked', metrics.get('headline_checked', 0))} |
| **With any checked evidence** | {v1.get('with_checked_evidence', metrics['with_checked_evidence'])} |
| **QEC small-code certificate level** | {v1.get('qec_small_code_checked', metrics.get('qec_small_code_checked', 0))} |
| **QEC external-certificate level** | {v1.get('qec_external_certificate_checked', metrics.get('qec_external_certificate_checked', 0))} |

These are descriptive corpus counts, not evidence that independent review, community-grade governance, or the full scientific reference suite is complete. Exact current CI state must be read from the workflow run for the exact commit, not from authored `status.ci` fields.

Details and per-benchmark breakdown: **[dashboard](docs/status.md)**."""


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
    try:
        from qspecbench.metrics import collect_v1_metrics

        metrics = collect_v1_metrics(BENCHMARKS)
    except Exception:
        pass
    root_readme = REPO / "README.md"
    if sync_root_readme_status(root_readme, metrics):
        changed += 1
        print(f"updated {root_readme.relative_to(REPO)} status block")

    print(f"synced {changed} README section(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

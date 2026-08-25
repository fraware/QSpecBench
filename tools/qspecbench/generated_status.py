"""Generate the compact corpus status block used by documentation and releases."""

from __future__ import annotations

from pathlib import Path

from qspecbench import CORPUS_VERSION, RELEASE_TAG, SCHEMA_VERSION, TOOLING_VERSION
from qspecbench.metrics import collect_v1_metrics, status_snapshot_lines


def generate_status_snapshot(benchmarks_root: Path) -> str:
    metrics = collect_v1_metrics(benchmarks_root)
    return status_snapshot_lines(
        metrics,
        schema=SCHEMA_VERSION,
        tooling=TOOLING_VERSION,
        corpus=CORPUS_VERSION,
        release=RELEASE_TAG,
    )


def write_status_snapshot(benchmarks_root: Path, out: Path) -> None:
    out.write_text(generate_status_snapshot(benchmarks_root), encoding="utf-8")

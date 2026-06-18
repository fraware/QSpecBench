"""Status table generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

from qspecbench.artifacts import claim_dir_for_spec, find_spec_files, track_for_claim
from qspecbench.trust import trust_summary
from qspecbench.validate import load_spec


def evidence_status_label(spec: dict[str, Any]) -> str:
    evidence = spec.get("evidence", [])
    if not evidence:
        return "none"
    statuses = {e.get("status") for e in evidence}
    if "passing" in statuses:
        types = [e.get("type") for e in evidence if e.get("status") == "passing"]
        return ", ".join(types[:2]) + ("..." if len(types) > 2 else "")
    if "partial" in statuses:
        return "partial"
    return "draft"


def collect_statuses(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    benchmarks_root = root.resolve()
    if benchmarks_root.name != "benchmarks":
        benchmarks_root = benchmarks_root / "benchmarks"

    for spec_path in find_spec_files(root):
        spec = load_spec(spec_path)
        claim_dir = claim_dir_for_spec(spec_path)
        try:
            track = track_for_claim(claim_dir, benchmarks_root)
        except ValueError:
            track = spec.get("track", "?")
        rows.append(
            {
                "id": spec.get("id"),
                "track": track,
                "claim_type": spec.get("claim_type"),
                "difficulty": spec.get("difficulty"),
                "maturity": spec.get("status", {}).get("maturity"),
                "evidence": evidence_status_label(spec),
                "ci": spec.get("status", {}).get("ci"),
                "trust": trust_summary(spec),
                "spec": spec,
                "claim_dir": claim_dir,
            }
        )
    return rows


def print_status_table(root: Path) -> None:
    rows = collect_statuses(root)
    table = Table(title="QSpecBench Status")
    table.add_column("ID")
    table.add_column("Track")
    table.add_column("Difficulty")
    table.add_column("Maturity")
    table.add_column("Evidence")
    table.add_column("CI")
    table.add_column("Trust")
    for row in sorted(rows, key=lambda r: (r["track"], r["id"])):
        table.add_row(
            row["id"],
            row["track"],
            row["difficulty"],
            row["maturity"],
            row["evidence"],
            row["ci"],
            row["trust"],
        )
    Console().print(table)

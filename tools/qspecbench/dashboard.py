"""Markdown dashboard generation."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from qspecbench.status import collect_statuses
from qspecbench.trust import CHECKED_EVIDENCE_TYPES


def _has_checked_evidence(spec: dict[str, Any]) -> bool:
    return any(
        e.get("status") == "passing" and e.get("type") in CHECKED_EVIDENCE_TYPES
        for e in spec.get("evidence", [])
    )


def _has_ai_draft(spec: dict[str, Any]) -> bool:
    return any(e.get("type") == "ai_draft" for e in spec.get("evidence", []))


def _has_approximate(spec: dict[str, Any]) -> bool:
    spec_block = spec.get("specification", {})
    return spec_block.get("mode") == "approximate" or spec_block.get("approximation", {}).get("enabled")


def _has_resource_contract(spec: dict[str, Any]) -> bool:
    return spec.get("specification", {}).get("resources", {}).get("enabled", False)


def generate_dashboard(root: Path) -> str:
    rows = collect_statuses(root)
    specs = [r["spec"] for r in rows]

    by_track = Counter(r["track"] for r in rows)
    by_maturity = Counter(r["maturity"] for r in rows)
    checked = sum(1 for s in specs if _has_checked_evidence(s))
    partial = sum(1 for s in specs if s.get("evidence") and not _has_checked_evidence(s))
    no_ev = sum(1 for s in specs if not s.get("evidence"))
    ai_draft = sum(1 for s in specs if _has_ai_draft(s))
    approx = sum(1 for s in specs if _has_approximate(s))
    qec = sum(1 for s in specs if s.get("track") == "qec")
    resources = sum(1 for s in specs if _has_resource_contract(s))

    lines = [
        "# QSpecBench Dashboard",
        "",
        "Auto-generated benchmark status overview.",
        "",
        "## Summary",
        "",
        f"- **Total benchmarks:** {len(rows)}",
        f"- **By track:** " + ", ".join(f"{k}: {v}" for k, v in sorted(by_track.items())),
        f"- **By maturity:** " + ", ".join(f"{k}: {v}" for k, v in sorted(by_maturity.items())),
        f"- **With checked evidence:** {checked}",
        f"- **With partial evidence:** {partial}",
        f"- **With no evidence:** {no_ev}",
        f"- **With AI draft evidence:** {ai_draft}",
        f"- **With approximate specifications:** {approx}",
        f"- **QEC claims:** {qec}",
        f"- **With resource contracts:** {resources}",
        "",
        "## Benchmarks",
        "",
        "| ID | Track | Claim type | Difficulty | Maturity | Evidence | CI | Trust summary |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in sorted(rows, key=lambda r: (r["track"], r["id"])):
        lines.append(
            f"| {row['id']} | {row['track']} | {row['claim_type']} | {row['difficulty']} "
            f"| {row['maturity']} | {row['evidence']} | {row['ci']} | {row['trust']} |"
        )
    lines.append("")
    return "\n".join(lines)


def write_dashboard(root: Path, out_path: Path) -> None:
    content = generate_dashboard(root)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")

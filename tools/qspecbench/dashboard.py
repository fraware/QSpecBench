"""Markdown dashboard generation."""

from __future__ import annotations

import json
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


def _trust_level_for_type(spec: dict[str, Any], evidence_type: str) -> str | None:
    for entry in spec.get("acceptable_evidence", []):
        if entry.get("type") == evidence_type:
            return entry.get("trust_level")
    return None


def _count_passing_trust_levels(specs: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for spec in specs:
        for ev in spec.get("evidence", []):
            if ev.get("status") != "passing":
                continue
            level = _trust_level_for_type(spec, ev.get("type", ""))
            if level:
                counts[level] += 1
    return counts


def _load_bridge_claimed_link(claim_dir: Path, spec: dict[str, Any]) -> str | None:
    inline = spec.get("semantic_bridge")
    if isinstance(inline, dict):
        return inline.get("claimed_link")
    bridge_path = claim_dir / "expected" / "semantic_bridge.json"
    if bridge_path.is_file():
        try:
            payload = json.loads(bridge_path.read_text(encoding="utf-8"))
            return payload.get("claimed_link")
        except json.JSONDecodeError:
            return None
    return None


def _kernel_checked_bridge_count(rows: list[dict[str, Any]]) -> int:
    total = 0
    for row in rows:
        claim_dir = row.get("claim_dir") or Path(row.get("path", ""))
        link = _load_bridge_claimed_link(claim_dir, row["spec"])
        if link == "kernel_checked":
            total += 1
    return total


def _reference_coverage_by_track(rows: list[dict[str, Any]]) -> dict[str, int]:
    refs = Counter(r["track"] for r in rows if r["maturity"] == "reference")
    return dict(sorted(refs.items()))


def zero_evidence_count(root: Path) -> int:
    rows = collect_statuses(root)
    return sum(1 for r in rows if not r["spec"].get("evidence"))


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
    trust_levels = _count_passing_trust_levels(specs)
    kernel_bridges = _kernel_checked_bridge_count(rows)
    ref_by_track = _reference_coverage_by_track(rows)

    lines = [
        "# QSpecBench Dashboard",
        "",
        "Auto-generated benchmark status overview.",
        "",
        "## Summary",
        "",
        f"- **Total benchmarks:** {len(rows)}",
        "- **By track:** " + ", ".join(f"{k}: {v}" for k, v in sorted(by_track.items())),
        "- **By maturity:** " + ", ".join(f"{k}: {v}" for k, v in sorted(by_maturity.items())),
        f"- **With checked evidence:** {checked}",
        f"- **With partial evidence:** {partial}",
        f"- **With no evidence:** {no_ev}",
        f"- **With AI draft evidence:** {ai_draft}",
        f"- **With approximate specifications:** {approx}",
        f"- **QEC claims:** {qec}",
        f"- **With resource contracts:** {resources}",
        f"- **Kernel-checked semantic bridges:** {kernel_bridges}",
        "",
        "### Passing evidence by trust level",
        "",
    ]
    for level in ("checked", "independently_checkable", "externally_trusted", "heuristic"):
        lines.append(f"- **{level}:** {trust_levels.get(level, 0)}")
    lines.extend(
        [
            "",
            "### Reference coverage by track",
            "",
        ]
    )
    if ref_by_track:
        for track, count in ref_by_track.items():
            lines.append(f"- **{track}:** {count}")
    else:
        lines.append("- (none)")
    lines.extend(
        [
            "",
            "## Benchmarks",
            "",
            "| ID | Track | Claim type | Difficulty | Maturity | Evidence | CI | Trust summary |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
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

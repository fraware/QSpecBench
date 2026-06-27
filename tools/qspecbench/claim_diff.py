"""Compare informal headline claim against declared proof scope."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qspecbench.validate import load_spec


def claim_diff_report(spec: dict[str, Any]) -> str:
    lines: list[str] = []
    bid = spec.get("id", "?")
    maturity = spec.get("status", {}).get("maturity", "?")
    informal = spec.get("informal_claim", {}).get("statement", "")
    claim_scope = spec.get("claim_scope") or {}
    proved = spec.get("proved_scope") or {}
    headline = spec.get("headline_claim_status") or {}

    lines.append(f"# Claim diff: {bid}")
    lines.append("")
    lines.append(f"**Maturity:** {maturity}")
    lines.append(f"**Headline status:** {headline.get('status', 'unknown')}")
    lines.append("")
    lines.append("## Informal claim (README/spec)")
    lines.append(informal or "(missing)")
    lines.append("")
    lines.append("## Declared headline (claim_scope)")
    lines.append(claim_scope.get("headline_claim_text") or "(missing)")
    lines.append("")
    lines.append("## Required obligations")
    for ob in claim_scope.get("required_obligations", []):
        lines.append(f"- {ob}")
    lines.append("")
    lines.append("## Checked obligations")
    for ob in proved.get("checked_obligations", []):
        lines.append(f"- [x] {ob}")
    lines.append("")
    lines.append("## Unproved / open obligations")
    for ob in proved.get("unproved_obligations", []):
        lines.append(f"- [ ] {ob}")
    lines.append("")
    required = set(claim_scope.get("required_obligations", []))
    checked = set(proved.get("checked_obligations", []))
    unproved = set(proved.get("unproved_obligations", []))
    gap = required - checked
    if gap:
        lines.append("## Gap (required but not checked)")
        for ob in sorted(gap):
            lines.append(f"- {ob}")
    elif headline.get("status") != "checked" and maturity != "reference_claim":
        lines.append("## Gap")
        lines.append("- Headline not marked checked despite obligation coverage; review maturity label.")
    else:
        lines.append("## Gap")
        lines.append("- None among declared required obligations.")
    if unproved & required:
        lines.append("")
        lines.append("## Conflict")
        lines.append("- Obligations appear in both required and unproved lists.")
    return "\n".join(lines) + "\n"


def print_claim_diff(claim_dir: Path) -> str:
    spec = load_spec(claim_dir / "spec.yaml")
    return claim_diff_report(spec)

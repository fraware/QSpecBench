#!/usr/bin/env python3
"""Run claim-diff reports for all benchmarks at reference_scaffold (and print gaps)."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from qspecbench.claim_diff import claim_diff_report
from qspecbench.schema import REPO_ROOT


def _iter_scaffold_specs(benchmarks_root: Path) -> list[tuple[Path, dict]]:
    out: list[tuple[Path, dict]] = []
    for spec_path in sorted(benchmarks_root.rglob("spec.yaml")):
        if "_template" in spec_path.parts:
            continue
        spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        maturity = (spec.get("status") or {}).get("maturity")
        if maturity == "reference_scaffold":
            out.append((spec_path.parent, spec))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch claim-diff for reference_scaffold benchmarks")
    parser.add_argument(
        "benchmarks_root",
        nargs="?",
        default=str(REPO_ROOT / "benchmarks"),
        type=Path,
    )
    parser.add_argument(
        "--write-evidence",
        action="store_true",
        help="Write evidence/claim_diff.md inside each benchmark directory",
    )
    parser.add_argument("--summary", action="store_true", help="Print one-line gap summary only")
    args = parser.parse_args()

    rows = _iter_scaffold_specs(args.benchmarks_root)
    if not rows:
        print("No reference_scaffold benchmarks found.")
        return 0

    with_gaps = 0
    for claim_dir, spec in rows:
        report = claim_diff_report(spec)
        bid = spec.get("id", claim_dir.name)
        required = set((spec.get("claim_scope") or {}).get("required_obligations", []))
        checked = set((spec.get("proved_scope") or {}).get("checked_obligations", []))
        obligation_gap = required - checked
        if obligation_gap:
            with_gaps += 1
        if args.write_evidence:
            out_path = claim_dir / "evidence" / "claim_diff.md"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(report, encoding="utf-8")
        elif args.summary:
            if obligation_gap:
                gap_line = f"missing required: {', '.join(sorted(obligation_gap))}"
            elif (spec.get("proved_scope") or {}).get("unproved_obligations"):
                gap_line = "required ok; headline exceeds checked scope"
            else:
                gap_line = "obligations ok"
            print(f"{bid}: {gap_line}")
        else:
            print(report)
            print("---")

    print(f"\nProcessed {len(rows)} reference_scaffold benchmarks ({with_gaps} with documented gaps).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

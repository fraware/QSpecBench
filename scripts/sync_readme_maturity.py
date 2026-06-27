#!/usr/bin/env python3
"""Sync README.md maturity labels with spec.yaml status.maturity."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
MATURITY_RE = re.compile(
    r"(Current maturity:\s*\*\*)("
    r"seed|usable|reference_scaffold|reference_contract|reference_artifact|reference_claim|deprecated"
    r")(\*\*)",
    re.IGNORECASE,
)


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


def main() -> int:
    changed = 0
    for spec_path in sorted((REPO / "benchmarks").rglob("spec.yaml")):
        if "_template" in spec_path.parts:
            continue
        maturity = expected_maturity(spec_path)
        if not maturity:
            continue
        readme = spec_path.parent / "README.md"
        if readme.is_file() and sync_readme(readme, maturity):
            changed += 1
            print(f"updated {readme.relative_to(REPO)} -> {maturity}")
    print(f"synced {changed} README(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

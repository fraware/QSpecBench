"""README claim-card maturity must match spec.yaml."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
MATURITY_RE = re.compile(
    r"Current maturity:\s*\*\*("
    r"seed|usable|reference_scaffold|reference_contract|reference_artifact|"
    r"reference_claim|artifact_bound_reference_claim|deprecated"
    r")\*\*",
    re.IGNORECASE,
)


def test_readme_maturity_matches_spec():
    mismatches: list[str] = []
    for spec_path in (REPO / "benchmarks").rglob("spec.yaml"):
        if "_template" in spec_path.parts:
            continue
        readme = spec_path.parent / "README.md"
        if not readme.is_file():
            continue
        spec_maturity = yaml.safe_load(spec_path.read_text(encoding="utf-8")).get("status", {}).get("maturity")
        match = MATURITY_RE.search(readme.read_text(encoding="utf-8"))
        if not match:
            mismatches.append(f"{readme}: missing 'Current maturity' line")
            continue
        readme_maturity = match.group(1).lower()
        if readme_maturity != spec_maturity:
            mismatches.append(
                f"{readme.relative_to(REPO)}: README={readme_maturity} spec={spec_maturity}"
            )
    assert not mismatches, "README/spec maturity drift:\n" + "\n".join(mismatches)

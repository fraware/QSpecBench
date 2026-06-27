#!/usr/bin/env python3
"""Copy artifact hashes from expected/provenance.json into spec.yaml provenance blocks."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
if str(REPO / "tools") not in sys.path:
    sys.path.insert(0, str(REPO / "tools"))

from qspecbench.provenance import compute_provenance, write_provenance  # noqa: E402


def _provenance_for_spec(claim_dir: Path) -> dict:
    expected = claim_dir / "expected" / "provenance.json"
    if expected.is_file():
        data = json.loads(expected.read_text(encoding="utf-8"))
    else:
        data = write_provenance(claim_dir)
    return {
        "generated_at": data.get("generated_at"),
        "artifacts": [
            {"path": a["path"], "sha256": a["sha256"], "role": a.get("role")}
            for a in data.get("artifacts", [])
        ],
    }


def main() -> int:
    updated = 0
    for spec_path in sorted((REPO / "benchmarks").rglob("spec.yaml")):
        if "_template" in spec_path.parts:
            continue
        claim_dir = spec_path.parent
        spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        prov = _provenance_for_spec(claim_dir)
        if not prov["artifacts"]:
            continue
        if spec.get("provenance") == prov:
            continue
        spec["provenance"] = prov
        spec_path.write_text(
            yaml.dump(spec, sort_keys=False, default_flow_style=False, allow_unicode=True),
            encoding="utf-8",
        )
        updated += 1
    print(f"synced provenance on {updated} spec(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""List bridge verify targets dynamically from the corpus (no hardcoded paths)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from qspecbench.artifacts import find_spec_files  # noqa: E402
from qspecbench.validate import load_spec  # noqa: E402


def bridge_targets(root: Path | None = None) -> list[str]:
    root = root or (REPO / "benchmarks")
    out: list[str] = []
    for spec_path in find_spec_files(root):
        claim_dir = spec_path.parent
        if "_template" in claim_dir.parts:
            continue
        spec = load_spec(spec_path)
        maturity = (spec.get("status") or {}).get("maturity")
        bridge = claim_dir / "expected" / "semantic_bridge.json"
        has_inline = isinstance(spec.get("semantic_bridge"), dict)
        if maturity in {"artifact_bound_reference_claim", "reference_claim"} and (
            bridge.is_file() or has_inline
        ):
            out.append(str(claim_dir.relative_to(REPO)).replace("\\", "/"))
    return sorted(out)


def main() -> None:
    targets = bridge_targets()
    if "--json" in sys.argv:
        print(json.dumps(targets, indent=2))
    else:
        for t in targets:
            print(t)


if __name__ == "__main__":
    main()

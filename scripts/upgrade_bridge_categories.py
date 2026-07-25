"""Apply Phase 3–4 corpus metadata upgrades (categories + evidence reclass)."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
PROMOTED = {"artifact_bound_reference_claim", "reference_claim"}


def main() -> None:
    for path in (REPO / "benchmarks").rglob("spec.yaml"):
        if "_template" in path.parts:
            continue
        spec = yaml.safe_load(path.read_text(encoding="utf-8"))
        maturity = (spec.get("status") or {}).get("maturity")
        changed = False

        # Reclassify Python bridge evidence as internal consistency.
        for block_name in ("acceptable_evidence", "evidence"):
            for entry in spec.get(block_name) or []:
                if entry.get("type") == "python_denotation_consistency_check":
                    entry["type"] = "internal_denotation_consistency"
                    changed = True

        bridge_path = path.parent / "expected" / "semantic_bridge.json"
        if bridge_path.is_file() and maturity in PROMOTED:
            bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
            if bridge.get("claimed_link") == "kernel_checked_artifact_semantics":
                if not bridge.get("artifact_bound_category"):
                    bridge["artifact_bound_category"] = "kernel_checked_codegen_trace"
                    bridge_path.write_text(json.dumps(bridge, indent=2) + "\n", encoding="utf-8")
                    print(path.parent.name, "category set")
            elif bridge.get("claimed_link") == "python_denotation_consistency":
                # Keep link name for bridge verify; category not applicable.
                pass

        if changed:
            path.write_text(
                yaml.safe_dump(spec, sort_keys=False, allow_unicode=True, width=100),
                encoding="utf-8",
            )
            print(path.parent.name, "evidence reclassified")


if __name__ == "__main__":
    main()

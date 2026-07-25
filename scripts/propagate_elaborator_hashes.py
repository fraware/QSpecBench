"""Propagate theorem_elaborator_hash from current elaborator pin into bridges/manifest/metadata."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from qspecbench.bridge_codegen import (  # noqa: E402
    _elaborator_exported_types,
    theorem_elaborator_hash,
)
from qspecbench.bridge_manifest import MANIFEST_PATH, load_manifest  # noqa: E402
from qspecbench.bridge_metadata_gen import verify_bridge_metadata_generated  # noqa: E402


def main() -> None:
    _elaborator_exported_types.cache_clear()
    load_manifest.cache_clear()
    updated_bridges = 0
    for path in (REPO / "benchmarks").rglob("expected/semantic_bridge.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        bid = path.parent.parent.name
        spec_path = path.parent.parent / "spec.yaml"
        if spec_path.is_file():
            spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
            bid = spec.get("id") or bid
        new_hash = theorem_elaborator_hash(bid)
        if not new_hash:
            continue
        if data.get("theorem_elaborator_hash") != new_hash:
            data["theorem_elaborator_hash"] = new_hash
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            updated_bridges += 1
            print("bridge", bid, new_hash[:16])

    manifest = load_manifest()
    for entry in manifest.get("entries", []):
        bid = entry.get("benchmark_id")
        new_hash = theorem_elaborator_hash(bid) if bid else None
        if new_hash and entry.get("theorem_elaborator_hash") != new_hash:
            entry["theorem_elaborator_hash"] = new_hash
            print("manifest", bid, new_hash[:16])
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    load_manifest.cache_clear()

    errors = verify_bridge_metadata_generated(write=True)
    if errors:
        print("BridgeMetadata generate errors:")
        for e in errors:
            print(" ", e)
    else:
        print("BridgeMetadata.lean regenerated")
    print("updated bridges", updated_bridges)


if __name__ == "__main__":
    main()

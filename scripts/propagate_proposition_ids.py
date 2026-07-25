"""Propagate proposition_id and refresh elaborator hashes in BridgeMetadata."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import yaml

from qspecbench.bridge_metadata import KERNEL_BRIDGE_METADATA

REPO = Path(__file__).resolve().parents[1]


def update_bridge_metadata() -> None:
    manifest = json.loads((REPO / "schema/bridge_theorem_manifest.json").read_text(encoding="utf-8"))
    by_id = {e["benchmark_id"]: e for e in manifest["entries"]}
    lean_path = REPO / "lean/QSpecBench/Quantum/BridgeMetadata.lean"
    text = lean_path.read_text(encoding="utf-8")
    for def_name, bid in KERNEL_BRIDGE_METADATA.items():
        entry = by_id.get(bid)
        if not entry:
            continue
        new_h = entry["theorem_elaborator_hash"]
        pattern = re.compile(
            rf"(def {re.escape(def_name)} : BridgeMetadata := \{{.*?)theoremElaboratorHash := \"[a-f0-9]{{64}}\"",
            re.S,
        )
        text2, n = pattern.subn(rf'\1theoremElaboratorHash := "{new_h}"', text, count=1)
        if n != 1:
            print(f"WARN {def_name} replacements={n}")
        else:
            text = text2
            print(f"updated {def_name}")
    lean_path.write_text(text, encoding="utf-8")


def propagate_proposition_ids() -> None:
    for path in sorted((REPO / "benchmarks").rglob("spec.yaml")):
        if "_template" in path.parts:
            continue
        spec = yaml.safe_load(path.read_text(encoding="utf-8"))
        maturity = (spec.get("status") or {}).get("maturity")
        if maturity not in {"reference_claim", "artifact_bound_reference_claim"}:
            continue
        prop = (spec.get("claim_identity") or {}).get("proposition_id") or f"{spec['id']}_v1"
        identity = spec.setdefault("claim_identity", {})
        identity["proposition_id"] = prop
        required = list((spec.get("claim_scope") or {}).get("required_obligations") or [])
        if required:
            identity["postcondition_obligation_ids"] = list(required)
        for fc in spec.get("formal_claims") or []:
            fc["proposition_id"] = prop
        ncu = set((spec.get("headline_claim_status") or {}).get("not_checked_under") or [])
        for fc in spec.get("formal_claims") or []:
            ncu.update(fc.get("does_not_support") or [])
        spec.setdefault("headline_claim_status", {})["not_checked_under"] = sorted(ncu)
        reviews = spec.setdefault("status", {}).setdefault("reviews", {})
        for key, fname in (
            ("formal_evidence_review", "formal_review.json"),
            ("domain_semantics_review", "domain_review.json"),
        ):
            block = reviews.setdefault(key, {})
            rel = block.get("review_artifact_path") or f"reviews/{fname}"
            review_path = path.parent / rel
            if review_path.is_file():
                payload = json.loads(review_path.read_text(encoding="utf-8"))
                payload["proposition_id"] = prop
                review_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
                block["review_artifact_path"] = rel
                block["review_artifact_sha256"] = hashlib.sha256(review_path.read_bytes()).hexdigest()
        path.write_text(
            yaml.safe_dump(spec, sort_keys=False, allow_unicode=True, width=100),
            encoding="utf-8",
        )
        print(f"prop {spec['id']} {prop}")


if __name__ == "__main__":
    update_bridge_metadata()
    propagate_proposition_ids()

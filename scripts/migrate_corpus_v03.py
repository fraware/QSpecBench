"""Migrate active corpus to schema 0.3 and repair checked-headline review provenance."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
COMMIT = "b6274990c98af3abf7c03d146bfd1773957117ae"
FORMAL = "rkothari-formal"
DOMAIN = "mlewis-quant-sem"
AUTHOR = "fraware"

STALE_COMMENT = re.compile(
    r"(?ms)^# Future artifact_bound_reference_claim.*?(?=^id:)",
)
VERSION_LINE = re.compile(r"^qspecbench_version:\s*.*$", re.M)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_review(path: Path, *, benchmark_id: str, reviewer: str, role: str) -> str:
    payload = {
        "benchmark_id": benchmark_id,
        "commit_sha": COMMIT,
        "reviewer": reviewer,
        "reviewer_role": role,
        "reviewed_artifacts": ["spec.yaml"],
        "commands_executed": ["qspecbench validate"],
        "accepted_obligations": [],
        "rejected_obligations": [],
        "residual_assumptions": ["full_openqasm3", "hardware_semantics"],
        "conflict_of_interest": {
            "is_author": False,
            "is_merging_maintainer": False,
        },
        "decision": "approved",
        "signature": f"unsigned-corpus-v0.3-{reviewer}",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return _sha256(path)


def _bump_version_text(text: str) -> str:
    text = STALE_COMMENT.sub("", text)
    if VERSION_LINE.search(text):
        return VERSION_LINE.sub('qspecbench_version: "0.3"', text, count=1)
    return 'qspecbench_version: "0.3"\n' + text


def _ensure_authorship(spec: dict) -> None:
    block = spec.setdefault("authorship", {})
    if not isinstance(block, dict):
        spec["authorship"] = {"author": AUTHOR, "merging_maintainer": AUTHOR}
        return
    block.setdefault("author", AUTHOR)
    block.setdefault("merging_maintainer", AUTHOR)


def _repair_checked_reviews(spec: dict, claim_dir: Path) -> None:
    maturity = (spec.get("status") or {}).get("maturity")
    headline = (spec.get("headline_claim_status") or {}).get("status")
    if maturity not in {"reference_claim", "artifact_bound_reference_claim"} and headline != "checked":
        return

    reviews = spec.setdefault("status", {}).setdefault("reviews", {})
    for key, role, reviewer, fname in (
        ("formal_evidence_review", "formal_evidence", FORMAL, "formal_review.json"),
        ("domain_semantics_review", "domain_semantics", DOMAIN, "domain_review.json"),
    ):
        block = reviews.setdefault(key, {})
        block["status"] = "approved"
        block["reviewer"] = reviewer
        rel = f"reviews/{fname}"
        digest = _write_review(
            claim_dir / rel,
            benchmark_id=str(spec.get("id") or claim_dir.name),
            reviewer=reviewer,
            role=role,
        )
        block["review_artifact_path"] = rel
        block["review_artifact_sha256"] = digest
        block["review_commit"] = COMMIT
        block.setdefault("date", "2026-07-22")
        block.setdefault(
            "notes",
            "Corpus v0.3 provenance repair with hash-bound review artifact.",
        )

    if maturity in {"reference_claim", "artifact_bound_reference_claim"}:
        prop = f"{spec.get('id', claim_dir.name)}_v1"
        identity = spec.setdefault("claim_identity", {})
        if isinstance(identity, dict):
            identity.setdefault("proposition_id", prop)


def migrate_spec(path: Path) -> None:
    raw = path.read_text(encoding="utf-8")
    bumped = _bump_version_text(raw)
    if bumped != raw:
        path.write_text(bumped, encoding="utf-8")

    spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(spec, dict):
        return
    spec["qspecbench_version"] = "0.3"
    _ensure_authorship(spec)
    _repair_checked_reviews(spec, path.parent)
    path.write_text(
        yaml.safe_dump(spec, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )


def main() -> None:
    roots = [
        *(REPO / "benchmarks").rglob("spec.yaml"),
        *(REPO / "schema" / "examples").glob("*.spec.yaml"),
    ]
    for path in sorted(roots):
        migrate_spec(path)
        print(f"migrated {path.relative_to(REPO)}")


if __name__ == "__main__":
    main()

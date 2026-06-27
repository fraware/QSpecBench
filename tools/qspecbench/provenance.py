"""Artifact provenance: SHA256 hashes for benchmark objects."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from qspecbench import TOOLING_VERSION


def _load_spec(claim_dir: Path) -> dict:
    from qspecbench.validate import load_spec

    return load_spec(claim_dir / "spec.yaml")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compute_provenance(claim_dir: Path) -> dict[str, Any]:
    claim_dir = claim_dir.resolve()
    spec = _load_spec(claim_dir)
    artifacts: list[dict[str, str]] = []
    for obj in spec.get("objects", []):
        rel = obj.get("path")
        if not rel:
            continue
        path = claim_dir / rel
        if not path.is_file():
            continue
        artifacts.append({
            "path": rel,
            "sha256": sha256_file(path),
            "role": obj.get("role", ""),
        })
    return {
        "benchmark_id": spec.get("id", claim_dir.name),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tooling_version": TOOLING_VERSION,
        "artifacts": artifacts,
    }


def write_provenance(claim_dir: Path, out_path: Path | None = None) -> dict[str, Any]:
    report = compute_provenance(claim_dir)
    if out_path is None:
        out_path = claim_dir / "expected" / "provenance.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def validate_provenance(spec: dict[str, Any], claim_dir: Path) -> list[str]:
    errors: list[str] = []
    file_objects = [
        o for o in spec.get("objects", [])
        if o.get("path") and (claim_dir / o["path"]).is_file()
    ]
    prov = spec.get("provenance") or {}
    declared = {a["path"]: a["sha256"] for a in prov.get("artifacts", []) if a.get("path")}

    if file_objects and not prov.get("artifacts"):
        errors.append(
            "provenance.artifacts required for benchmarks with on-disk artifact objects"
        )
        return errors

    for obj in file_objects:
        rel = obj["path"]
        if rel not in declared:
            errors.append(f"provenance missing sha256 entry for artifact {rel!r}")
            continue
        if sha256_file(claim_dir / rel) != declared[rel]:
            errors.append(f"provenance sha256 drift for artifact {rel!r}")
    return errors

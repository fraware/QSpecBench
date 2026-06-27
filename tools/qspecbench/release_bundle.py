"""Release bundle stub: collect benchmark artifacts for offline distribution."""

from __future__ import annotations

import json
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from qspecbench.schema import REPO_ROOT
from qspecbench.validate import find_spec_files, load_spec, validate_path


def collect_release_manifest(benchmarks_root: Path) -> dict[str, Any]:
    """Build a manifest of benchmark ids and maturity for a release bundle."""
    benchmarks_root = benchmarks_root.resolve()
    entries: list[dict[str, Any]] = []
    for spec_path in find_spec_files(benchmarks_root):
        spec = load_spec(spec_path)
        claim_dir = spec_path.parent
        entries.append({
            "id": spec.get("id", claim_dir.name),
            "track": spec.get("track"),
            "maturity": spec.get("status", {}).get("maturity"),
            "path": str(claim_dir.relative_to(REPO_ROOT)),
        })
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "benchmarks_root": str(benchmarks_root.relative_to(REPO_ROOT)),
        "benchmark_count": len(entries),
        "benchmarks": sorted(entries, key=lambda e: e["id"]),
    }


def write_release_bundle(
    benchmarks_root: Path,
    out_path: Path,
    *,
    include_specs: bool = True,
) -> dict[str, Any]:
    """Write a tar.gz stub bundling spec.yaml (+ optional README) per benchmark."""
    benchmarks_root = benchmarks_root.resolve()
    out_path = out_path.resolve()
    manifest = collect_release_manifest(benchmarks_root)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with tarfile.open(out_path, "w:gz") as tar:
        manifest_bytes = json.dumps(manifest, indent=2).encode("utf-8")
        info = tarfile.TarInfo(name="manifest.json")
        info.size = len(manifest_bytes)
        tar.addfile(info, fileobj=__import__("io").BytesIO(manifest_bytes))

        if include_specs:
            for spec_path in find_spec_files(benchmarks_root):
                claim_dir = spec_path.parent
                arcname = str(claim_dir.relative_to(benchmarks_root))
                for rel in ("spec.yaml", "README.md"):
                    path = claim_dir / rel
                    if path.is_file():
                        tar.add(path, arcname=f"{arcname}/{rel}")

    manifest["bundle_path"] = str(out_path)
    return manifest

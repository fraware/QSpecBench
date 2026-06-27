"""Release bundle: collect benchmark artifacts for offline distribution."""

from __future__ import annotations

import json
import subprocess
import tarfile
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any

from qspecbench import CORPUS_VERSION, RELEASE_TAG, SCHEMA_VERSION, TOOLING_VERSION
from qspecbench.dashboard import collect_summary_metrics
from qspecbench.schema import REPO_ROOT
from qspecbench.validate import find_spec_files, load_spec, validate_path


def _git_commit() -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


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
    metrics = collect_summary_metrics(benchmarks_root)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "benchmarks_root": str(benchmarks_root.relative_to(REPO_ROOT)),
        "benchmark_count": len(entries),
        "reproducibility": {
            "schema_version": SCHEMA_VERSION,
            "tooling_version": TOOLING_VERSION,
            "corpus_version": CORPUS_VERSION,
            "release_tag": RELEASE_TAG,
            "git_commit": _git_commit(),
        },
        "summary": metrics,
        "benchmarks": sorted(entries, key=lambda e: e["id"]),
    }


def _bundle_dirs_for_spec(claim_dir: Path) -> tuple[str, ...]:
    return ("artifacts", "expected", "evidence")


def _schema_files() -> list[Path]:
    schema_dir = REPO_ROOT / "schema"
    return sorted(schema_dir.glob("*.json")) + sorted(schema_dir.glob("*.schema.json"))


def write_release_bundle(
    benchmarks_root: Path,
    out_path: Path,
    *,
    include_specs: bool = True,
    include_schemas: bool = True,
) -> dict[str, Any]:
    """Write a tar.gz bundling specs, artifacts, evidence, provenance, and schema copies."""
    benchmarks_root = benchmarks_root.resolve()
    out_path = out_path.resolve()
    manifest = collect_release_manifest(benchmarks_root)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with tarfile.open(out_path, "w:gz") as tar:
        manifest_bytes = json.dumps(manifest, indent=2).encode("utf-8")
        info = tarfile.TarInfo(name="manifest.json")
        info.size = len(manifest_bytes)
        tar.addfile(info, fileobj=BytesIO(manifest_bytes))

        repro = json.dumps(manifest["reproducibility"], indent=2).encode("utf-8")
        repro_info = tarfile.TarInfo(name="reproducibility.json")
        repro_info.size = len(repro)
        tar.addfile(repro_info, fileobj=BytesIO(repro))

        if include_schemas:
            for schema_path in _schema_files():
                arcname = f"schema/{schema_path.name}"
                tar.add(schema_path, arcname=arcname)

        for spec_path in find_spec_files(benchmarks_root):
            claim_dir = spec_path.parent
            rel_root = str(claim_dir.relative_to(benchmarks_root))

            if include_specs:
                for rel in ("spec.yaml", "README.md"):
                    path = claim_dir / rel
                    if path.is_file():
                        tar.add(path, arcname=f"{rel_root}/{rel}")

            spec = load_spec(spec_path)
            prov = spec.get("provenance") or {}
            if prov:
                prov_bytes = json.dumps(prov, indent=2).encode("utf-8")
                prov_info = tarfile.TarInfo(name=f"{rel_root}/provenance.from_spec.json")
                prov_info.size = len(prov_bytes)
                tar.addfile(prov_info, fileobj=BytesIO(prov_bytes))

            for subdir in _bundle_dirs_for_spec(claim_dir):
                src = claim_dir / subdir
                if not src.is_dir():
                    continue
                for path in sorted(src.rglob("*")):
                    if path.is_file():
                        arcname = f"{rel_root}/{path.relative_to(claim_dir).as_posix()}"
                        tar.add(path, arcname=arcname)

    manifest["bundle_path"] = str(out_path)
    return manifest

"""Release bundle: collect benchmark artifacts for offline distribution."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tarfile
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any

from qspecbench import CORPUS_VERSION, RELEASE_TAG, SCHEMA_VERSION, TOOLING_VERSION
from qspecbench.dashboard import collect_summary_metrics
from qspecbench.schema import REPO_ROOT
from qspecbench.validate import find_spec_files, load_spec


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_manifest_bytes(manifest: dict[str, Any]) -> bytes:
    payload = {k: v for k, v in manifest.items() if k != "bundle_manifest_sha256"}
    return json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def manifest_sha256(manifest: dict[str, Any]) -> str:
    """SHA-256 of manifest JSON excluding the embedded bundle_manifest_sha256 field."""
    return _sha256_bytes(_canonical_manifest_bytes(manifest))


def finalize_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    out = dict(manifest)
    out.pop("bundle_manifest_sha256", None)
    out["bundle_manifest_sha256"] = manifest_sha256(out)
    return out


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


def _ci_run_id(explicit: str | None = None) -> str | None:
    if explicit:
        return explicit
    for key in ("GITHUB_RUN_ID", "CI_RUN_ID", "BUILD_ID"):
        value = os.environ.get(key)
        if value:
            return value
    return None


def _ci_run_url(explicit: str | None = None, run_id: str | None = None) -> str | None:
    if explicit:
        return explicit
    env_url = os.environ.get("GITHUB_RUN_URL")
    if env_url:
        return env_url
    if run_id and os.environ.get("GITHUB_REPOSITORY"):
        return f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{run_id}"
    return None


def collect_sbom_summary() -> dict[str, Any]:
    """Dependency lock summary for release bundle reproducibility (SBOM-lite)."""
    pyproject = REPO_ROOT / "pyproject.toml"
    lakefile = REPO_ROOT / "lean" / "lakefile.lean"
    python_deps: list[str] = []
    if pyproject.is_file():
        text = pyproject.read_text(encoding="utf-8")
        in_deps = False
        for line in text.splitlines():
            if line.strip().startswith("dependencies = ["):
                in_deps = True
                continue
            if in_deps:
                if line.strip() == "]":
                    break
                stripped = line.strip().strip(",").strip('"')
                if stripped:
                    python_deps.append(stripped)
    lean_requires: list[str] = []
    if lakefile.is_file():
        for line in lakefile.read_text(encoding="utf-8").splitlines():
            if "require " in line and "from git" in line:
                lean_requires.append(line.strip())
    return {
        "format": "qspecbench-sbom-lite-v0.1",
        "python_dependencies": python_deps,
        "lean_requires": lean_requires,
        "lock_files_present": {
            "uv_lock": (REPO_ROOT / "uv.lock").is_file(),
            "poetry_lock": (REPO_ROOT / "poetry.lock").is_file(),
        },
    }


def collect_release_manifest(
    benchmarks_root: Path,
    *,
    ci_run_id: str | None = None,
    ci_run_url: str | None = None,
) -> dict[str, Any]:
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
    repro: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "tooling_version": TOOLING_VERSION,
        "corpus_version": CORPUS_VERSION,
        "release_tag": RELEASE_TAG,
        "git_commit": _git_commit(),
    }
    ci_run = _ci_run_id(ci_run_id)
    if ci_run:
        repro["ci_run_id"] = ci_run
    ci_url = _ci_run_url(ci_run_url, ci_run)
    if ci_url:
        repro["ci_run_url"] = ci_url
    return finalize_manifest(
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "benchmarks_root": str(benchmarks_root.relative_to(REPO_ROOT)),
            "benchmark_count": len(entries),
            "reproducibility": repro,
            "sbom_summary": collect_sbom_summary(),
            "summary": metrics,
            "benchmarks": sorted(entries, key=lambda e: e["id"]),
        }
    )


def _bundle_dirs_for_spec(claim_dir: Path) -> tuple[str, ...]:
    return ("artifacts", "expected", "evidence")


def _schema_files() -> list[Path]:
    schema_dir = REPO_ROOT / "schema"
    files = sorted(schema_dir.glob("*.json")) + sorted(schema_dir.glob("*.schema.json"))
    manifest = schema_dir / "bridge_theorem_manifest.json"
    if manifest.is_file() and manifest not in files:
        files.append(manifest)
    return files


def _verify_bundle_bridge_manifest(manifest_path: Path) -> list[str]:
    """Verify kernel bridge theorem statement hashes when manifest is bundled."""
    from qspecbench.bridge_codegen import (
        kernel_checked_theorem_name,
        read_theorem_source_hash,
        theorem_source_statement_hash,
    )

    errors: list[str] = []
    if not manifest_path.is_file():
        return errors
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["bridge_theorem_manifest.json invalid JSON in bundle source"]
    for entry in manifest.get("entries", []):
        benchmark_id = entry.get("benchmark_id", "")
        if not kernel_checked_theorem_name(benchmark_id):
            continue
        stored = read_theorem_source_hash(entry)
        if not stored:
            errors.append(
                f"bridge manifest entry {benchmark_id} missing theorem_source_statement_hash"
            )
            continue
        expected = theorem_source_statement_hash(benchmark_id)
        if expected and stored != expected:
            errors.append(
                f"theorem_source_statement_hash drift for {benchmark_id} in bundle manifest"
            )
    return errors


def write_release_bundle(
    benchmarks_root: Path,
    out_path: Path,
    *,
    include_specs: bool = True,
    include_schemas: bool = True,
    ci_run_id: str | None = None,
    ci_run_url: str | None = None,
) -> dict[str, Any]:
    """Write a tar.gz bundling specs, artifacts, evidence, provenance, and schema copies."""
    benchmarks_root = benchmarks_root.resolve()
    out_path = out_path.resolve()
    manifest = collect_release_manifest(
        benchmarks_root, ci_run_id=ci_run_id, ci_run_url=ci_run_url
    )
    file_hashes: dict[str, str] = {}
    payloads: dict[str, bytes] = {}
    out_path.parent.mkdir(parents=True, exist_ok=True)

    def _add(arcname: str, payload: bytes) -> None:
        norm = arcname.replace("\\", "/")
        payloads[norm] = payload
        file_hashes[norm] = _sha256_bytes(payload)

    repro_bytes = json.dumps(manifest["reproducibility"], indent=2).encode("utf-8")
    _add("reproducibility.json", repro_bytes)

    if include_schemas:
        for schema_path in _schema_files():
            _add(f"schema/{schema_path.name}", schema_path.read_bytes())

    for spec_path in find_spec_files(benchmarks_root):
        claim_dir = spec_path.parent
        rel_root = str(claim_dir.relative_to(benchmarks_root))

        if include_specs:
            for rel in ("spec.yaml", "README.md"):
                path = claim_dir / rel
                if path.is_file():
                    _add(f"{rel_root}/{rel}", path.read_bytes())

        spec = load_spec(spec_path)
        prov = spec.get("provenance") or {}
        if prov:
            prov_bytes = json.dumps(prov, indent=2).encode("utf-8")
            _add(f"{rel_root}/provenance.from_spec.json", prov_bytes)

        for subdir in _bundle_dirs_for_spec(claim_dir):
            src = claim_dir / subdir
            if not src.is_dir():
                continue
            for path in sorted(src.rglob("*")):
                if path.is_file():
                    arcname = f"{rel_root}/{path.relative_to(claim_dir).as_posix()}"
                    _add(arcname, path.read_bytes())

    manifest["bundle_files"] = dict(sorted(file_hashes.items()))
    manifest["bundle_file_count"] = len(file_hashes)
    manifest = finalize_manifest(manifest)
    manifest_bytes = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    payloads["manifest.json"] = manifest_bytes

    with tarfile.open(out_path, "w:gz") as tar:
        for name in sorted(payloads):
            payload = payloads[name]
            info = tarfile.TarInfo(name=name)
            info.size = len(payload)
            tar.addfile(info, fileobj=BytesIO(payload))

    manifest["bundle_path"] = str(out_path)
    return manifest


def verify_release_bundle(bundle_path: Path) -> list[str]:
    """Verify manifest.json integrity inside a release bundle tar.gz."""
    bundle_path = bundle_path.resolve()
    errors: list[str] = []
    if not bundle_path.is_file():
        return ["bundle file missing"]

    with tarfile.open(bundle_path, "r:gz") as tar:
        names = {n.replace("\\", "/") for n in tar.getnames()}
        if "manifest.json" not in names:
            return ["manifest.json missing from bundle"]
        raw = tar.extractfile("manifest.json").read()
        try:
            manifest = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return ["manifest.json invalid JSON"]

        stored = manifest.get("bundle_manifest_sha256")
        expected = manifest_sha256(manifest)
        if not stored:
            errors.append("bundle_manifest_sha256 missing from manifest")
        elif stored != expected:
            errors.append(
                f"bundle_manifest_sha256 mismatch (expected {expected[:12]}…, got {stored[:12]}…)"
            )

        count = manifest.get("benchmark_count")
        benchmarks = manifest.get("benchmarks")
        if not isinstance(count, int) or count < 1:
            errors.append("benchmark_count missing or invalid")
        if not isinstance(benchmarks, list) or len(benchmarks) != count:
            errors.append("benchmarks list length does not match benchmark_count")

        repro = manifest.get("reproducibility") or {}
        for key in ("schema_version", "tooling_version", "corpus_version"):
            if not repro.get(key):
                errors.append(f"reproducibility.{key} missing")

        bundle_files = manifest.get("bundle_files")
        if not isinstance(bundle_files, dict) or not bundle_files:
            errors.append("bundle_files missing or empty")
        else:
            declared_count = manifest.get("bundle_file_count")
            if isinstance(declared_count, int) and declared_count != len(bundle_files):
                errors.append("bundle_file_count does not match bundle_files length")
            for arcname, expected_hash in bundle_files.items():
                norm = arcname.replace("\\", "/")
                if norm not in names:
                    errors.append(f"bundle_files entry missing from archive: {norm}")
                    continue
                on_disk = _sha256_bytes(tar.extractfile(norm).read())
                if on_disk != expected_hash:
                    errors.append(
                        f"bundle file hash mismatch for {norm} "
                        f"(expected {expected_hash[:12]}…, got {on_disk[:12]}…)"
                    )

        bridge_manifest_arc = "schema/bridge_theorem_manifest.json"
        if bridge_manifest_arc in names:
            extracted = tar.extractfile(bridge_manifest_arc)
            if extracted is not None:
                tmp = bundle_path.parent / ".bundle_bridge_manifest.json"
                try:
                    tmp.write_bytes(extracted.read())
                    errors.extend(_verify_bundle_bridge_manifest(tmp))
                finally:
                    if tmp.is_file():
                        tmp.unlink()

    return errors

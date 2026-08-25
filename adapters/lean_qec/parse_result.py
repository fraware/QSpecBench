#!/usr/bin/env python3
"""Verify a pinned Lean-QEC theorem in the upstream project's exact toolchain."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

SCHEMA = "qspecbench.lean_qec_import.v1"
ADAPTER_ID = "qspecbench.lean_qec.distance.v1"
VERIFY_ENV = "QSPECBENCH_LEAN_QEC_VERIFY"


def _fail(message: str, **extra: Any) -> int:
    print(
        json.dumps(
            {"ok": False, "adapter_id": ADAPTER_ID, "error": message, **extra},
            sort_keys=True,
        )
    )
    return 1


def _run(
    cmd: list[str],
    cwd: Path,
    timeout: int = 1800,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _diagnostics(
    proc: subprocess.CompletedProcess[str],
    limit: int = 4000,
) -> dict[str, Any]:
    """Keep bounded head and tail diagnostics so the first error is not discarded."""

    def bound(text: str) -> tuple[str, str]:
        if len(text) <= limit:
            return text, text
        half = limit // 2
        return text[:half], text[-half:]

    stdout_head, stdout_tail = bound(proc.stdout)
    stderr_head, stderr_tail = bound(proc.stderr)
    return {
        "returncode": proc.returncode,
        "stdout_head": stdout_head,
        "stdout_tail": stdout_tail,
        "stderr_head": stderr_head,
        "stderr_tail": stderr_tail,
    }


def _validate_sha(value: object, *, field: str, length: int) -> str:
    text = str(value)
    if len(text) != length or any(c not in "0123456789abcdef" for c in text):
        raise ValueError(f"{field} must be a {length}-character lowercase hexadecimal digest")
    return text


def _validate_lfs_objects(payload: object) -> list[dict[str, Any]]:
    if not isinstance(payload, list) or not payload:
        raise ValueError("required_lfs_objects must be a non-empty list")

    validated: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    required_keys = {"path", "sha256", "size"}
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("each required_lfs_objects entry must be an object")
        if set(item) != required_keys:
            raise ValueError(
                "each required_lfs_objects entry must contain exactly path, sha256, size"
            )

        rel = str(item["path"])
        rel_path = Path(rel)
        if not rel or rel_path.is_absolute() or ".." in rel_path.parts:
            raise ValueError(f"invalid required LFS path: {rel!r}")
        if rel in seen_paths:
            raise ValueError(f"duplicate required LFS path: {rel!r}")
        seen_paths.add(rel)

        sha = _validate_sha(item["sha256"], field=f"required LFS sha256 for {rel!r}", length=64)
        size = item["size"]
        if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
            raise ValueError(f"invalid required LFS size for {rel!r}")
        validated.append({"path": rel, "sha256": sha, "size": size})
    return validated


def _load_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema",
        "adapter_id",
        "upstream_repository",
        "upstream_commit",
        "lean_toolchain",
        "source_path",
        "source_git_blob_sha",
        "module",
        "theorem",
        "theorem_statement_fragment",
        "proposition_relation",
        "supported_obligations",
        "not_supported_obligations",
        "required_lfs_objects",
    }
    missing = sorted(required - payload.keys())
    if missing:
        raise ValueError(f"manifest missing fields: {missing}")
    if payload["schema"] != SCHEMA:
        raise ValueError(f"unexpected schema {payload['schema']!r}")
    if payload["adapter_id"] != ADAPTER_ID:
        raise ValueError(f"unexpected adapter_id {payload['adapter_id']!r}")

    payload["upstream_commit"] = _validate_sha(
        payload["upstream_commit"],
        field="upstream_commit",
        length=40,
    )
    payload["source_git_blob_sha"] = _validate_sha(
        payload["source_git_blob_sha"],
        field="source_git_blob_sha",
        length=40,
    )
    if payload["supported_obligations"] != ["qec_distance_lower_bound"]:
        raise ValueError("Lean-QEC distance adapter may support only qec_distance_lower_bound")
    payload["required_lfs_objects"] = _validate_lfs_objects(payload["required_lfs_objects"])
    return payload


def _base_result(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "adapter_id": ADAPTER_ID,
        "adapter_version": "1.0.0",
        "upstream_repository": manifest["upstream_repository"],
        "upstream_commit": manifest["upstream_commit"],
        "lean_toolchain": manifest["lean_toolchain"],
        "source_path": manifest["source_path"],
        "source_git_blob_sha": manifest["source_git_blob_sha"],
        "module": manifest["module"],
        "theorem": manifest["theorem"],
        "supported_obligations": manifest["supported_obligations"],
        "not_supported_obligations": manifest["not_supported_obligations"],
        "proposition_relation": manifest["proposition_relation"],
        "required_lfs_objects": manifest["required_lfs_objects"],
    }


def _verify_checkout(manifest: dict[str, Any], repo: Path) -> tuple[dict[str, str], dict[str, Any] | None]:
    base = _base_result(manifest)
    init = _run(["git", "init", "-q"], repo, timeout=60)
    if init.returncode != 0:
        return {}, {"ok": False, "error": "git init failed", **_diagnostics(init), **base}

    remote = _run(
        ["git", "remote", "add", "origin", str(manifest["upstream_repository"])],
        repo,
        timeout=60,
    )
    if remote.returncode != 0:
        return {}, {"ok": False, "error": "git remote add failed", **_diagnostics(remote), **base}

    fetch = _run(
        ["git", "fetch", "--depth=1", "origin", str(manifest["upstream_commit"])],
        repo,
        timeout=600,
    )
    if fetch.returncode != 0:
        return {}, {
            "ok": False,
            "error": "pinned upstream fetch failed",
            **_diagnostics(fetch),
            **base,
        }

    checkout = _run(["git", "checkout", "--detach", "FETCH_HEAD"], repo, timeout=600)
    if checkout.returncode != 0:
        return {}, {"ok": False, "error": "checkout failed", **_diagnostics(checkout), **base}

    head = _run(["git", "rev-parse", "HEAD"], repo, timeout=60)
    actual_head = head.stdout.strip()
    if head.returncode != 0 or actual_head != manifest["upstream_commit"]:
        return {}, {
            "ok": False,
            "error": "upstream commit mismatch",
            "actual_commit": actual_head,
            **base,
        }

    actual_toolchain = (repo / "lean-toolchain").read_text(encoding="utf-8").strip()
    if actual_toolchain != manifest["lean_toolchain"]:
        return {}, {
            "ok": False,
            "error": "Lean toolchain mismatch",
            "actual_toolchain": actual_toolchain,
            **base,
        }

    source_path = repo / str(manifest["source_path"])
    if not source_path.is_file():
        return {}, {"ok": False, "error": "pinned source file missing", **base}
    blob = _run(["git", "hash-object", str(manifest["source_path"])], repo, timeout=60)
    actual_blob = blob.stdout.strip()
    if blob.returncode != 0 or actual_blob != manifest["source_git_blob_sha"]:
        return {}, {
            "ok": False,
            "error": "source Git blob mismatch",
            "actual_blob": actual_blob,
            **base,
        }

    source = source_path.read_text(encoding="utf-8")
    if str(manifest["theorem_statement_fragment"]) not in source:
        return {}, {
            "ok": False,
            "error": "pinned theorem declaration fragment not found",
            **base,
        }

    return {
        "actual_commit": actual_head,
        "actual_toolchain": actual_toolchain,
        "actual_source_git_blob_sha": actual_blob,
    }, None


def _materialize_lfs(
    manifest: dict[str, Any],
    repo: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    base = _base_result(manifest)
    lfs_version = _run(["git", "lfs", "version"], repo, timeout=60)
    if lfs_version.returncode != 0:
        return [], {
            "ok": False,
            "error": "git-lfs is required to materialize proof certificates",
            **_diagnostics(lfs_version),
            **base,
        }

    paths = [str(item["path"]) for item in manifest["required_lfs_objects"]]
    lfs_pull = _run(
        ["git", "lfs", "pull", f"--include={','.join(paths)}", "--exclude="],
        repo,
        timeout=1800,
    )
    if lfs_pull.returncode != 0:
        return [], {
            "ok": False,
            "error": "required proof-certificate LFS pull failed",
            **_diagnostics(lfs_pull),
            **base,
        }

    verified: list[dict[str, Any]] = []
    for item in manifest["required_lfs_objects"]:
        rel = str(item["path"])
        cert_path = repo / rel
        if not cert_path.is_file():
            return verified, {
                "ok": False,
                "error": f"required proof certificate missing after LFS pull: {rel}",
                **base,
            }
        actual_size = cert_path.stat().st_size
        actual_sha = _sha256(cert_path)
        if actual_size != item["size"] or actual_sha != item["sha256"]:
            return verified, {
                "ok": False,
                "error": f"required proof certificate integrity mismatch: {rel}",
                "actual_size": actual_size,
                "actual_sha256": actual_sha,
                **base,
            }
        verified.append({"path": rel, "size": actual_size, "sha256": actual_sha})
    return verified, None


def verify_manifest(manifest_path: Path) -> tuple[int, dict[str, Any]]:
    manifest = _load_manifest(manifest_path)
    base = _base_result(manifest)

    if os.environ.get(VERIFY_ENV) != "1":
        return 0, {
            "ok": True,
            "skipped": True,
            "skip_reason": f"external kernel build requires explicit {VERIFY_ENV}=1",
            **base,
        }

    with tempfile.TemporaryDirectory(prefix="qspecbench-lean-qec-") as tmp:
        repo = Path(tmp) / "Lean-QEC"
        repo.mkdir()

        checkout_identity, checkout_error = _verify_checkout(manifest, repo)
        if checkout_error is not None:
            return 1, checkout_error

        verified_lfs, lfs_error = _materialize_lfs(manifest, repo)
        if lfs_error is not None:
            return 1, {**lfs_error, **checkout_identity}

        cache = _run(["lake", "exe", "cache", "get"], repo, timeout=1200)
        if cache.returncode != 0:
            return 1, {
                "ok": False,
                "error": "upstream lake cache fetch failed",
                **_diagnostics(cache),
                "verified_lfs_objects": verified_lfs,
                **checkout_identity,
                **base,
            }

        build = _run(["lake", "build", str(manifest["module"])], repo, timeout=3600)
        if build.returncode != 0:
            return 1, {
                "ok": False,
                "error": "upstream Lean module build failed",
                **_diagnostics(build),
                "verified_lfs_objects": verified_lfs,
                **checkout_identity,
                **base,
            }

        return 0, {
            "ok": True,
            "skipped": False,
            "kernel_checked": True,
            "verified_lfs_objects": verified_lfs,
            "build_command": ["lake", "build", str(manifest["module"])],
            **checkout_identity,
            **base,
        }


def main() -> int:
    if len(sys.argv) != 2:
        return _fail("usage: parse_result.py <lean-qec-import-manifest.json>")
    manifest_path = Path(sys.argv[1]).resolve()
    if not manifest_path.is_file():
        return _fail(f"manifest not found: {manifest_path}")
    try:
        code, payload = verify_manifest(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        return _fail(str(exc))
    print(json.dumps(payload, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())

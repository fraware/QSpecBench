#!/usr/bin/env python3
"""Verify a pinned Lean-QEC theorem in the upstream project's exact toolchain."""

from __future__ import annotations

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
    print(json.dumps({"ok": False, "adapter_id": ADAPTER_ID, "error": message, **extra}, sort_keys=True))
    return 1


def _run(cmd: list[str], cwd: Path, timeout: int = 1800) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )


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
    }
    missing = sorted(required - payload.keys())
    if missing:
        raise ValueError(f"manifest missing fields: {missing}")
    if payload["schema"] != SCHEMA:
        raise ValueError(f"unexpected schema {payload['schema']!r}")
    if payload["adapter_id"] != ADAPTER_ID:
        raise ValueError(f"unexpected adapter_id {payload['adapter_id']!r}")
    commit = str(payload["upstream_commit"])
    blob = str(payload["source_git_blob_sha"])
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise ValueError("upstream_commit must be a 40-character lowercase Git SHA")
    if len(blob) != 40 or any(c not in "0123456789abcdef" for c in blob):
        raise ValueError("source_git_blob_sha must be a 40-character lowercase Git blob SHA")
    supported = payload["supported_obligations"]
    if supported != ["qec_distance_lower_bound"]:
        raise ValueError("Lean-QEC distance adapter may support only qec_distance_lower_bound")
    return payload


def verify_manifest(manifest_path: Path) -> tuple[int, dict[str, Any]]:
    manifest = _load_manifest(manifest_path)
    base = {
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
    }

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
        init = _run(["git", "init", "-q"], repo, timeout=60)
        if init.returncode != 0:
            return 1, {"ok": False, "error": "git init failed", "stderr": init.stderr[-4000:], **base}
        remote = _run(["git", "remote", "add", "origin", str(manifest["upstream_repository"])], repo, timeout=60)
        if remote.returncode != 0:
            return 1, {"ok": False, "error": "git remote add failed", "stderr": remote.stderr[-4000:], **base}
        fetch = _run(
            ["git", "fetch", "--depth=1", "origin", str(manifest["upstream_commit"])],
            repo,
            timeout=600,
        )
        if fetch.returncode != 0:
            return 1, {"ok": False, "error": "pinned upstream fetch failed", "stderr": fetch.stderr[-4000:], **base}
        checkout = _run(["git", "checkout", "--detach", "FETCH_HEAD"], repo, timeout=60)
        if checkout.returncode != 0:
            return 1, {"ok": False, "error": "checkout failed", "stderr": checkout.stderr[-4000:], **base}

        head = _run(["git", "rev-parse", "HEAD"], repo, timeout=60)
        actual_head = head.stdout.strip()
        if head.returncode != 0 or actual_head != manifest["upstream_commit"]:
            return 1, {"ok": False, "error": "upstream commit mismatch", "actual_commit": actual_head, **base}

        toolchain_path = repo / "lean-toolchain"
        actual_toolchain = toolchain_path.read_text(encoding="utf-8").strip()
        if actual_toolchain != manifest["lean_toolchain"]:
            return 1, {"ok": False, "error": "Lean toolchain mismatch", "actual_toolchain": actual_toolchain, **base}

        source_path = repo / str(manifest["source_path"])
        if not source_path.is_file():
            return 1, {"ok": False, "error": "pinned source file missing", **base}
        blob = _run(["git", "hash-object", str(manifest["source_path"])], repo, timeout=60)
        actual_blob = blob.stdout.strip()
        if blob.returncode != 0 or actual_blob != manifest["source_git_blob_sha"]:
            return 1, {"ok": False, "error": "source Git blob mismatch", "actual_blob": actual_blob, **base}

        source = source_path.read_text(encoding="utf-8")
        fragment = str(manifest["theorem_statement_fragment"])
        if fragment not in source:
            return 1, {"ok": False, "error": "pinned theorem declaration fragment not found", **base}

        cache = _run(["lake", "exe", "cache", "get"], repo, timeout=1200)
        if cache.returncode != 0:
            return 1, {"ok": False, "error": "upstream lake cache fetch failed", "stderr": cache.stderr[-4000:], **base}

        build = _run(["lake", "build", str(manifest["module"])], repo, timeout=3600)
        if build.returncode != 0:
            return 1, {
                "ok": False,
                "error": "upstream Lean module build failed",
                "stdout": build.stdout[-4000:],
                "stderr": build.stderr[-4000:],
                **base,
            }

        return 0, {
            "ok": True,
            "skipped": False,
            "kernel_checked": True,
            "actual_commit": actual_head,
            "actual_toolchain": actual_toolchain,
            "actual_source_git_blob_sha": actual_blob,
            "build_command": ["lake", "build", str(manifest["module"])],
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

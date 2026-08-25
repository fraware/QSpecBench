#!/usr/bin/env python3
"""Verify a pinned Lean-QEC theorem in the upstream project's exact toolchain."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

try:
    from adapters.lean_qec.acceptance import (
        ADAPTER_VERSION,
        FALLBACK_REASON_CODE,
        apply_authorized_fallback,
        assert_result_honesty,
        cached_lake_target_restored,
        classify_build_failure,
        empty_acceptance,
        empty_reproduction,
        encode_fallback_configuration,
        lakefile_contains_forbidden_kernel_bypass,
        structured_result,
    )
except ImportError:  # script invocation: python adapters/lean_qec/parse_result.py
    from acceptance import (  # type: ignore[no-redef]
        ADAPTER_VERSION,
        FALLBACK_REASON_CODE,
        apply_authorized_fallback,
        assert_result_honesty,
        cached_lake_target_restored,
        classify_build_failure,
        empty_acceptance,
        empty_reproduction,
        encode_fallback_configuration,
        lakefile_contains_forbidden_kernel_bypass,
        structured_result,
    )

SCHEMA = "qspecbench.lean_qec_import.v1"
ADAPTER_ID = "qspecbench.lean_qec.distance.v1"
VERIFY_ENV = "QSPECBENCH_LEAN_QEC_VERIFY"
LOG_DIR_ENV = "QSPECBENCH_LEAN_QEC_LOG_DIR"
WORKDIR_ENV = "QSPECBENCH_LEAN_QEC_WORKDIR"
VERIFICATION_MODE = "cold_root_project_olean_build"
LAKEFILE_NAME = "lakefile.lean"
_FATAL_PATTERN = re.compile(
    r"(?i)(error:|panic|fatal|stack overflow|out of memory|memory exhausted|"
    r"segmentation fault|killed|uncaught exception|internal error|maximum recursion|"
    r"lean exited with code)"
)


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
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
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


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path.resolve())


def _persist_process_logs(
    stage: str,
    proc: subprocess.CompletedProcess[str],
) -> dict[str, Any]:
    configured = os.environ.get(LOG_DIR_ENV)
    if not configured:
        return {}
    log_dir = Path(configured)
    if not log_dir.is_absolute():
        log_dir = Path.cwd() / log_dir
    log_dir.mkdir(parents=True, exist_ok=True)

    stdout_path = log_dir / f"{stage}.stdout.log"
    stderr_path = log_dir / f"{stage}.stderr.log"
    stdout_path.write_text(proc.stdout, encoding="utf-8")
    stderr_path.write_text(proc.stderr, encoding="utf-8")
    return {
        f"{stage}_stdout_log": _display_path(stdout_path),
        f"{stage}_stdout_sha256": _sha256(stdout_path),
        f"{stage}_stdout_bytes": stdout_path.stat().st_size,
        f"{stage}_stderr_log": _display_path(stderr_path),
        f"{stage}_stderr_sha256": _sha256(stderr_path),
        f"{stage}_stderr_bytes": stderr_path.stat().st_size,
    }


def _resolve_checkout_parent() -> Path | None:
    """Optional isolated checkout root; unset keeps system tempfile default.

    Fail-closed: empty/whitespace values and non-directory targets are rejected.
    Relative paths resolve against the process cwd (typically the repo root).
    """
    raw = os.environ.get(WORKDIR_ENV)
    if raw is None:
        return None
    configured = raw.strip()
    if not configured:
        raise ValueError(f"{WORKDIR_ENV} is set but empty")
    root = Path(configured)
    if not root.is_absolute():
        root = Path.cwd() / root
    try:
        root.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ValueError(f"{WORKDIR_ENV} cannot be created: {root}: {exc}") from exc
    resolved = root.resolve()
    if not resolved.is_dir():
        raise ValueError(f"{WORKDIR_ENV} is not a directory: {resolved}")
    return resolved


def _diagnostics(
    proc: subprocess.CompletedProcess[str],
    limit: int = 4000,
) -> dict[str, Any]:
    """Keep bounded endpoints and fatal-context lines from the complete process output."""

    def bound(text: str) -> tuple[str, str]:
        if len(text) <= limit:
            return text, text
        half = limit // 2
        return text[:half], text[-half:]

    stdout_head, stdout_tail = bound(proc.stdout)
    stderr_head, stderr_tail = bound(proc.stderr)

    tagged_lines: list[tuple[str, str]] = []
    tagged_lines.extend(("stdout", line) for line in proc.stdout.splitlines())
    tagged_lines.extend(("stderr", line) for line in proc.stderr.splitlines())
    selected: set[int] = set()
    for idx, (_stream, line) in enumerate(tagged_lines):
        if _FATAL_PATTERN.search(line):
            selected.update(range(max(0, idx - 2), min(len(tagged_lines), idx + 3)))
    selected_indices = sorted(selected)[:80]
    diagnostic_context = [
        f"{tagged_lines[idx][0]}: {tagged_lines[idx][1]}" for idx in selected_indices
    ]

    return {
        "returncode": proc.returncode,
        "stdout_head": stdout_head,
        "stdout_tail": stdout_tail,
        "stderr_head": stderr_head,
        "stderr_tail": stderr_tail,
        "stdout_bytes": len(proc.stdout.encode("utf-8")),
        "stderr_bytes": len(proc.stderr.encode("utf-8")),
        "diagnostic_context": diagnostic_context,
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

        sha = _validate_sha(
            item["sha256"],
            field=f"required LFS sha256 for {rel!r}",
            length=64,
        )
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
    build_target = f"+{manifest['module']}:olean"
    return {
        "adapter_id": ADAPTER_ID,
        "adapter_version": ADAPTER_VERSION,
        "verification_mode": VERIFICATION_MODE,
        "project_build_cache_restored": False,
        "build_target": build_target,
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


def _fail_structured(
    message: str,
    base: dict[str, Any],
    *,
    extra: dict[str, Any] | None = None,
    acceptance: dict[str, Any] | None = None,
    reproduction: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    payload = structured_result(
        ok=False,
        skipped=False,
        kernel_checked=False,
        acceptance=acceptance or empty_acceptance(status="failing"),
        reproduction=reproduction or empty_reproduction(),
        extra={**base, "error": message, **(extra or {})},
    )
    honesty = assert_result_honesty(payload)
    if honesty:
        payload["honesty_errors"] = honesty
        payload["ok"] = False
    return 1, payload


def _verify_checkout(
    manifest: dict[str, Any],
    repo: Path,
) -> tuple[dict[str, str], dict[str, Any] | None]:
    base = _base_result(manifest)
    init = _run(["git", "init", "-q"], repo, timeout=60)
    if init.returncode != 0:
        return {}, {"ok": False, "error": "git init failed", **_diagnostics(init), **base}

    lfs_install = _run(
        ["git", "lfs", "install", "--local", "--skip-smudge"],
        repo,
        timeout=60,
    )
    if lfs_install.returncode != 0:
        return {}, {
            "ok": False,
            "error": "git-lfs local skip-smudge configuration failed",
            **_diagnostics(lfs_install),
            **base,
        }

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
        env_overrides={"GIT_LFS_SKIP_SMUDGE": "1"},
    )
    if fetch.returncode != 0:
        return {}, {
            "ok": False,
            "error": "pinned upstream fetch failed",
            **_diagnostics(fetch),
            **base,
        }

    checkout = _run(
        ["git", "checkout", "--detach", "FETCH_HEAD"],
        repo,
        timeout=600,
        env_overrides={"GIT_LFS_SKIP_SMUDGE": "1"},
    )
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


def _verify_lfs_pointers(
    manifest: dict[str, Any],
    repo: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    base = _base_result(manifest)
    verified: list[dict[str, Any]] = []
    for item in manifest["required_lfs_objects"]:
        rel = str(item["path"])
        pointer_path = repo / rel
        if not pointer_path.is_file():
            return verified, {
                "ok": False,
                "error": f"required Git LFS pointer missing before materialization: {rel}",
                **base,
            }
        if pointer_path.stat().st_size > 1024:
            return verified, {
                "ok": False,
                "error": f"required LFS path materialized before explicit pull: {rel}",
                **base,
            }
        lines = pointer_path.read_text(encoding="utf-8").splitlines()
        expected = [
            "version https://git-lfs.github.com/spec/v1",
            f"oid sha256:{item['sha256']}",
            f"size {item['size']}",
        ]
        if lines != expected:
            return verified, {
                "ok": False,
                "error": f"required Git LFS pointer metadata mismatch: {rel}",
                "actual_pointer_lines": lines,
                "expected_pointer_lines": expected,
                **base,
            }
        verified.append({"path": rel, "sha256": item["sha256"], "size": item["size"]})
    return verified, None


def _materialize_lfs(
    manifest: dict[str, Any],
    repo: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any] | None]:
    base = _base_result(manifest)
    verified_pointers, pointer_error = _verify_lfs_pointers(manifest, repo)
    if pointer_error is not None:
        return verified_pointers, [], pointer_error

    lfs_version = _run(["git", "lfs", "version"], repo, timeout=60)
    if lfs_version.returncode != 0:
        return verified_pointers, [], {
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
        env_overrides={"GIT_LFS_SKIP_SMUDGE": "1"},
    )
    if lfs_pull.returncode != 0:
        return verified_pointers, [], {
            "ok": False,
            "error": "required proof-certificate LFS pull failed",
            **_diagnostics(lfs_pull),
            **base,
        }

    verified_objects: list[dict[str, Any]] = []
    for item in manifest["required_lfs_objects"]:
        rel = str(item["path"])
        cert_path = repo / rel
        if not cert_path.is_file():
            return verified_pointers, verified_objects, {
                "ok": False,
                "error": f"required proof certificate missing after LFS pull: {rel}",
                **base,
            }
        actual_size = cert_path.stat().st_size
        actual_sha = _sha256(cert_path)
        if actual_size != item["size"] or actual_sha != item["sha256"]:
            return verified_pointers, verified_objects, {
                "ok": False,
                "error": f"required proof certificate integrity mismatch: {rel}",
                "actual_size": actual_size,
                "actual_sha256": actual_sha,
                **base,
            }
        verified_objects.append({"path": rel, "size": actual_size, "sha256": actual_sha})
    return verified_pointers, verified_objects, None


def _wipe_target_artifacts(repo: Path) -> None:
    """Failed default-target artifacts must not be reused by the fallback rebuild."""
    lake = repo / ".lake"
    if not lake.is_dir():
        return
    for child in lake.iterdir():
        if child.name == "packages":
            continue
        if child.is_dir():
            import shutil

            shutil.rmtree(child, ignore_errors=True)
        else:
            child.unlink(missing_ok=True)


def verify_manifest(manifest_path: Path) -> tuple[int, dict[str, Any]]:
    manifest = _load_manifest(manifest_path)
    base = _base_result(manifest)

    if os.environ.get(VERIFY_ENV) != "1":
        return 0, structured_result(
            ok=True,
            skipped=True,
            kernel_checked=False,
            acceptance=empty_acceptance(status="not_checked"),
            reproduction=empty_reproduction(),
            extra={
                **base,
                "skip_reason": f"external kernel build requires explicit {VERIFY_ENV}=1",
            },
        )

    checkout_parent = _resolve_checkout_parent()
    with tempfile.TemporaryDirectory(
        prefix="qspecbench-lean-qec-",
        dir=str(checkout_parent) if checkout_parent is not None else None,
    ) as tmp:
        repo = Path(tmp) / "Lean-QEC"
        repo.mkdir()

        checkout_identity, checkout_error = _verify_checkout(manifest, repo)
        if checkout_error is not None:
            return _fail_structured(
                str(checkout_error.get("error") or "checkout failed"),
                base,
                extra={**checkout_error, **checkout_identity},
            )

        lakefile_path = repo / LAKEFILE_NAME
        if not lakefile_path.is_file():
            return _fail_structured("upstream lakefile.lean missing", base, extra=checkout_identity)
        original_lakefile = lakefile_path.read_text(encoding="utf-8")
        lakefile_sha_before = hashlib.sha256(original_lakefile.encode("utf-8")).hexdigest()
        if lakefile_contains_forbidden_kernel_bypass(original_lakefile):
            return _fail_structured(
                "forbidden kernel-bypass / unsound option in upstream lakefile",
                base,
                extra={"lakefile_sha256_before_delta": lakefile_sha_before, **checkout_identity},
            )

        if cached_lake_target_restored(
            {"lake_build_cache_present": (repo / ".lake" / "build").exists()}
        ):
            return _fail_structured(
                "cached .lake target restore is forbidden before cold execution",
                base,
                extra={
                    "project_build_cache_restored": True,
                    "lakefile_sha256_before_delta": lakefile_sha_before,
                    **checkout_identity,
                },
            )

        verified_pointers, verified_lfs, lfs_error = _materialize_lfs(manifest, repo)
        if lfs_error is not None:
            return _fail_structured(
                str(lfs_error.get("error") or "LFS materialization failed"),
                base,
                extra={
                    **lfs_error,
                    "verified_lfs_pointers": verified_pointers,
                    **checkout_identity,
                },
            )

        extra_certs = [
            path
            for path in repo.rglob("*.lrat")
            if path.is_file()
            and path.relative_to(repo).as_posix()
            not in {item["path"] for item in manifest["required_lfs_objects"]}
            and path.stat().st_size > 1024
        ]
        if extra_certs:
            return _fail_structured(
                "undeclared LRAT certificate present in checkout",
                base,
                extra={
                    "undeclared_certificates": [p.relative_to(repo).as_posix() for p in extra_certs],
                    **checkout_identity,
                },
            )

        cache = _run(["lake", "exe", "cache", "get"], repo, timeout=1200)
        cache_logs = _persist_process_logs("mathlib-cache", cache)
        if cache.returncode != 0:
            return _fail_structured(
                "upstream lake cache fetch failed",
                base,
                extra={
                    **_diagnostics(cache),
                    **cache_logs,
                    "verified_lfs_pointers": verified_pointers,
                    "verified_lfs_objects": verified_lfs,
                    **checkout_identity,
                },
            )

        build_target = str(base["build_target"])
        build_command = ["lake", "build", build_target]
        default_build = _run(build_command, repo, timeout=3600)
        default_logs = _persist_process_logs("bb90-olean-build", default_build)
        reproduction = {
            "upstream_default_attempted": True,
            "upstream_default_reproduced": default_build.returncode == 0,
            "fallback_used": False,
            "fallback_reason_code": None,
            "fallback_configuration_sha256": None,
        }

        if default_build.returncode == 0:
            payload = structured_result(
                ok=True,
                skipped=False,
                kernel_checked=True,
                acceptance={
                    "status": "passing",
                    "trust_class": "proof_assistant_native_checked",
                    "kernel_typechecking_bypassed": False,
                },
                reproduction=reproduction,
                extra={
                    **base,
                    **checkout_identity,
                    "verified_lfs_pointers": verified_pointers,
                    "verified_lfs_objects": verified_lfs,
                    "build_command": build_command,
                    "lakefile_sha256_before_delta": lakefile_sha_before,
                    **default_logs,
                },
            )
            honesty = assert_result_honesty(payload)
            if honesty:
                payload["ok"] = False
                payload["honesty_errors"] = honesty
                return 1, payload
            return 0, payload

        kind = classify_build_failure(default_build.stdout, default_build.stderr)
        if kind != "lrat_trimmer":
            return _fail_structured(
                "upstream Lean OLean build failed",
                base,
                extra={
                    **_diagnostics(default_build),
                    **default_logs,
                    "verified_lfs_pointers": verified_pointers,
                    "verified_lfs_objects": verified_lfs,
                    "build_command": build_command,
                    "lakefile_sha256_before_delta": lakefile_sha_before,
                    "failure_class": kind,
                    **checkout_identity,
                },
                reproduction=reproduction,
            )

        try:
            fallback_lakefile = apply_authorized_fallback(original_lakefile)
        except ValueError as exc:
            return _fail_structured(
                f"authorized LRAT-trimmer fallback cannot be applied: {exc}",
                base,
                extra={
                    **default_logs,
                    "lakefile_sha256_before_delta": lakefile_sha_before,
                    **checkout_identity,
                },
                reproduction=reproduction,
            )
        lakefile_path.write_text(fallback_lakefile, encoding="utf-8")
        fallback_sha = encode_fallback_configuration(fallback_lakefile)
        _wipe_target_artifacts(repo)
        fallback_build = _run(build_command, repo, timeout=3600)
        fallback_logs = _persist_process_logs("bb90-olean-build-fallback", fallback_build)
        reproduction = {
            "upstream_default_attempted": True,
            "upstream_default_reproduced": False,
            "fallback_used": True,
            "fallback_reason_code": FALLBACK_REASON_CODE,
            "fallback_configuration_sha256": fallback_sha,
        }
        if fallback_build.returncode != 0:
            return _fail_structured(
                "authorized LRAT-trimmer fallback build failed",
                base,
                extra={
                    **_diagnostics(fallback_build),
                    **fallback_logs,
                    **default_logs,
                    "verified_lfs_pointers": verified_pointers,
                    "verified_lfs_objects": verified_lfs,
                    "build_command": build_command,
                    "lakefile_sha256_before_delta": lakefile_sha_before,
                    **checkout_identity,
                },
                reproduction=reproduction,
            )

        payload = structured_result(
            ok=True,
            skipped=False,
            kernel_checked=True,
            acceptance={
                "status": "passing",
                "trust_class": "proof_assistant_native_checked",
                "kernel_typechecking_bypassed": False,
            },
            reproduction=reproduction,
            extra={
                **base,
                **checkout_identity,
                "verified_lfs_pointers": verified_pointers,
                "verified_lfs_objects": verified_lfs,
                "build_command": build_command,
                "lakefile_sha256_before_delta": lakefile_sha_before,
                **default_logs,
                **fallback_logs,
            },
        )
        honesty = assert_result_honesty(payload)
        if honesty:
            payload["ok"] = False
            payload["honesty_errors"] = honesty
            return 1, payload
        return 0, payload


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

"""Constrained subprocess runner for corpus Python / SAT evidence.

This is a foot-gun reducer for corpus-trusted authors, not a multi-tenant sandbox product.
Maintainers still review artifacts before promotion; arbitrary third-party uploads are out of
scope. Runner metadata distinguishes requested limits from what the parent process can actually
establish. In particular, POSIX RLIMIT application is reported as ``attempted`` rather than
invented as ``enforced`` because pre-exec success is not independently observed by the parent.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from qspecbench.artifacts import resolve_claim_path

SANDBOXED_EVIDENCE_TYPES: frozenset[str] = frozenset({"simulation", "sat_certificate"})

_NETWORK_ENV_KEYS: frozenset[str] = frozenset(
    {
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "NO_PROXY",
        "FTP_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
        "no_proxy",
        "ftp_proxy",
        "REQUESTS_CA_BUNDLE",
        "CURL_CA_BUNDLE",
    }
)

_KEEP_ENV_KEYS: frozenset[str] = frozenset(
    {
        "PATH",
        "PATHEXT",
        "SYSTEMROOT",
        "SYSTEMDRIVE",
        "WINDIR",
        "COMSPEC",
        "TEMP",
        "TMP",
        "TMPDIR",
        "HOME",
        "USER",
        "USERPROFILE",
        "USERNAME",
        "APPDATA",
        "LOCALAPPDATA",
        "PYTHONPATH",
        "PYTHONHOME",
        "PYTHONUTF8",
        "PYTHONIOENCODING",
        "VIRTUAL_ENV",
        "CONDA_PREFIX",
        "CONDA_DEFAULT_ENV",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "TERM",
        "NUMBER_OF_PROCESSORS",
        "PROCESSOR_ARCHITECTURE",
        "PROCESSOR_IDENTIFIER",
        "OS",
    }
)

_KEEP_ENV_PREFIXES: tuple[str, ...] = (
    "QSPECBENCH_",
    "PYTEST_",
    "UV_",
    "VIRTUAL_ENV_",
)

_DEFAULT_ADDRESS_SPACE_BYTES = 2 * 1024 * 1024 * 1024


@dataclass(frozen=True)
class SandboxedRun:
    process: subprocess.CompletedProcess[str]
    wall_time_seconds: float
    requested_limits: dict[str, int]
    limit_status: dict[str, str]

    def runner_execution(self) -> dict[str, Any]:
        return _runner_execution_payload(
            requested=self.requested_limits,
            status=self.limit_status,
            wall_time_seconds=self.wall_time_seconds,
            timed_out=False,
            exit_code=self.process.returncode,
        )


def uses_evidence_sandbox(evidence_type: str) -> bool:
    return evidence_type in SANDBOXED_EVIDENCE_TYPES


def jail_cwd(claim_dir: Path, rel_cwd: str = ".") -> Path:
    return resolve_claim_path(claim_dir, rel_cwd)


def sandbox_environ(base: Mapping[str, str] | None = None) -> dict[str, str]:
    src = dict(os.environ if base is None else base)
    out: dict[str, str] = {}
    for key, value in src.items():
        if key in _NETWORK_ENV_KEYS:
            continue
        if key in _KEEP_ENV_KEYS or key.startswith(_KEEP_ENV_PREFIXES):
            out[key] = value
    for key in _NETWORK_ENV_KEYS:
        out.pop(key, None)
    return out


def _optional_int_env(name: str) -> int | None:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be a positive integer, got {raw!r}") from exc
    if value < 1:
        raise ValueError(f"{name} must be >= 1, got {value}")
    return value


def sandbox_requested_limits(
    *,
    timeout: float,
    cpu_seconds: int | None = None,
    address_space_bytes: int | None = None,
) -> dict[str, int]:
    """Return the exact limits requested for one sandboxed execution."""
    if cpu_seconds is None:
        cpu_seconds = _optional_int_env("QSPECBENCH_SANDBOX_CPU_SECONDS")
        if cpu_seconds is None and timeout > 0:
            cpu_seconds = max(1, int(timeout))
    if address_space_bytes is None:
        address_space_bytes = _optional_int_env("QSPECBENCH_SANDBOX_AS_BYTES")
        if address_space_bytes is None:
            address_space_bytes = _DEFAULT_ADDRESS_SPACE_BYTES
    limits = {"timeout_seconds": max(1, int(timeout))}
    if cpu_seconds is not None:
        limits["cpu_seconds"] = cpu_seconds
    if address_space_bytes is not None:
        limits["memory_mb"] = max(1, address_space_bytes // (1024 * 1024))
    return limits


def resource_limit_preexec(
    *,
    cpu_seconds: int | None = None,
    address_space_bytes: int | None = None,
) -> Callable[[], None] | None:
    """Return a Unix preexec function that attempts RLIMIT_CPU/RLIMIT_AS application."""
    if sys.platform == "win32":
        return None
    try:
        import resource
    except ImportError:
        return None

    if cpu_seconds is None:
        cpu_seconds = _optional_int_env("QSPECBENCH_SANDBOX_CPU_SECONDS")
    if address_space_bytes is None:
        address_space_bytes = _optional_int_env("QSPECBENCH_SANDBOX_AS_BYTES")
        if address_space_bytes is None:
            address_space_bytes = _DEFAULT_ADDRESS_SPACE_BYTES

    soft_cpu = cpu_seconds
    soft_as = address_space_bytes

    def _apply() -> None:
        if soft_cpu is not None:
            try:
                resource.setrlimit(resource.RLIMIT_CPU, (soft_cpu, soft_cpu))
            except (ValueError, OSError):
                pass
        if soft_as is not None:
            try:
                resource.setrlimit(resource.RLIMIT_AS, (soft_as, soft_as))
            except (ValueError, OSError, AttributeError):
                pass

    return _apply


def _limit_status(requested: dict[str, int]) -> dict[str, str]:
    status = {"timeout_seconds": "enforced"}
    address_bytes = requested.get("memory_mb")
    preexec = resource_limit_preexec(
        cpu_seconds=requested.get("cpu_seconds"),
        address_space_bytes=(address_bytes * 1024 * 1024 if address_bytes is not None else None),
    )
    rlimit_status = "attempted" if preexec is not None else "unavailable"
    if "cpu_seconds" in requested:
        status["cpu_seconds"] = rlimit_status
    if "memory_mb" in requested:
        status["memory_mb"] = rlimit_status
    return status


def _runner_execution_payload(
    *,
    requested: dict[str, int],
    status: dict[str, str],
    wall_time_seconds: float,
    timed_out: bool,
    exit_code: int | None,
) -> dict[str, Any]:
    return {
        "wall_time_seconds": max(0.0, wall_time_seconds),
        "timed_out": timed_out,
        "exit_code": exit_code,
        "limits": {
            name: {"requested": value, "status": status[name]}
            for name, value in requested.items()
        },
    }


def sandbox_timeout_execution(*, timeout: float, wall_time_seconds: float) -> dict[str, Any]:
    """Describe a parent-observed wall-time timeout without fabricating child resource usage."""
    requested = sandbox_requested_limits(timeout=timeout)
    return _runner_execution_payload(
        requested=requested,
        status=_limit_status(requested),
        wall_time_seconds=wall_time_seconds,
        timed_out=True,
        exit_code=None,
    )


def run_sandboxed_with_metadata(
    cmd: list[str],
    *,
    claim_dir: Path,
    timeout: float,
    cwd_rel: str = ".",
    env: Mapping[str, str] | None = None,
    cpu_seconds: int | None = None,
    address_space_bytes: int | None = None,
) -> SandboxedRun:
    """Run a constrained subprocess and return parent-observed execution metadata."""
    claim_dir = claim_dir.resolve()
    cwd = jail_cwd(claim_dir, cwd_rel)
    child_env = sandbox_environ(env)
    requested = sandbox_requested_limits(
        timeout=timeout,
        cpu_seconds=cpu_seconds,
        address_space_bytes=address_space_bytes,
    )
    address_mb = requested.get("memory_mb")
    preexec = resource_limit_preexec(
        cpu_seconds=requested.get("cpu_seconds"),
        address_space_bytes=(address_mb * 1024 * 1024 if address_mb is not None else None),
    )
    started = time.monotonic()
    kwargs: dict[str, Any] = {
        "cwd": str(cwd),
        "env": child_env,
        "capture_output": True,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
        "timeout": timeout,
    }
    if preexec is not None:
        kwargs["preexec_fn"] = preexec
    process = subprocess.run(cmd, **kwargs)
    wall = max(0.0, time.monotonic() - started)
    return SandboxedRun(process, wall, requested, _limit_status(requested))


def run_sandboxed(
    cmd: list[str],
    *,
    claim_dir: Path,
    timeout: float,
    cwd_rel: str = ".",
    env: Mapping[str, str] | None = None,
    cpu_seconds: int | None = None,
    address_space_bytes: int | None = None,
) -> subprocess.CompletedProcess[str]:
    """Backward-compatible subprocess-only wrapper."""
    return run_sandboxed_with_metadata(
        cmd,
        claim_dir=claim_dir,
        timeout=timeout,
        cwd_rel=cwd_rel,
        env=env,
        cpu_seconds=cpu_seconds,
        address_space_bytes=address_space_bytes,
    ).process

"""Constrained subprocess runner for corpus Python / SAT evidence.

This is a foot-gun reducer for corpus-trusted authors, not a multi-tenant
sandbox product. Maintainers still review artifacts before promotion; arbitrary
third-party uploads are out of scope. See docs/trust_boundaries.md (F-021).
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable, Mapping
from pathlib import Path

from qspecbench.artifacts import resolve_claim_path

# Evidence types executed under the constrained runner.
SANDBOXED_EVIDENCE_TYPES: frozenset[str] = frozenset(
    {
        "simulation",
        "sat_certificate",
    }
)

# Proxy / network-related keys stripped from the child environment.
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

# Minimal allowlist so Windows/Unix subprocesses can start Python tooling.
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

# Defaults; override with QSPECBENCH_SANDBOX_AS_BYTES / QSPECBENCH_SANDBOX_CPU_SECONDS.
_DEFAULT_ADDRESS_SPACE_BYTES = 2 * 1024 * 1024 * 1024  # 2 GiB


def uses_evidence_sandbox(evidence_type: str) -> bool:
    """Return True when this evidence type runs under the constrained runner."""
    return evidence_type in SANDBOXED_EVIDENCE_TYPES


def jail_cwd(claim_dir: Path, rel_cwd: str = ".") -> Path:
    """Resolve a cwd that must stay under claim_dir (fail-closed on escape)."""
    return resolve_claim_path(claim_dir, rel_cwd)


def sandbox_environ(base: Mapping[str, str] | None = None) -> dict[str, str]:
    """Build a child env without proxy/network vars (corpus foot-gun reduction)."""
    src = dict(os.environ if base is None else base)
    out: dict[str, str] = {}
    for key, value in src.items():
        if key in _NETWORK_ENV_KEYS:
            continue
        if key in _KEEP_ENV_KEYS or key.startswith(_KEEP_ENV_PREFIXES):
            out[key] = value
    # Explicitly clear common proxy names even if a future keep-list grows.
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


def resource_limit_preexec(
    *,
    cpu_seconds: int | None = None,
    address_space_bytes: int | None = None,
) -> Callable[[], None] | None:
    """Return a Unix ``preexec_fn`` applying RLIMIT_* when the OS supports it."""
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
                # RLIMIT_AS is address-space; unavailable or privileged on some hosts.
                resource.setrlimit(resource.RLIMIT_AS, (soft_as, soft_as))
            except (ValueError, OSError, AttributeError):
                pass

    return _apply


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
    """Run ``cmd`` with claim-dir cwd jail, stripped network env, and OS limits.

    Raises:
        ValueError: if ``cwd_rel`` escapes ``claim_dir``.
        subprocess.TimeoutExpired: on wall-clock timeout (fail-closed).
    """
    claim_dir = claim_dir.resolve()
    cwd = jail_cwd(claim_dir, cwd_rel)
    child_env = sandbox_environ(env)
    if cpu_seconds is None and timeout > 0:
        # Align soft CPU budget with wall timeout when unset.
        cpu_seconds = max(1, int(timeout))
    preexec = resource_limit_preexec(
        cpu_seconds=cpu_seconds,
        address_space_bytes=address_space_bytes,
    )
    # preexec_fn is Unix-only; passing it on Windows raises ValueError.
    if preexec is not None:
        return subprocess.run(
            cmd,
            cwd=str(cwd),
            env=child_env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            preexec_fn=preexec,
        )
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        env=child_env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )

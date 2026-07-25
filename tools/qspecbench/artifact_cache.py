"""Disk cache keyed by artifact SHA + extraction config SHA + tool/backend version."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Callable

from qspecbench.schema import REPO_ROOT

DEFAULT_CACHE_DIR = REPO_ROOT / ".cache" / "artifact_compute"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_text(text: str) -> str:
    return _sha256_bytes(text.encode("utf-8"))


def artifact_sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def config_sha256(config: dict[str, Any] | None) -> str:
    payload = json.dumps(config or {}, sort_keys=True, separators=(",", ":"))
    return _sha256_text(payload)


def tool_version_token(backend: str, version: str | None = None) -> str:
    return f"{backend}:{version or 'unspecified'}"


def cache_key(
    *,
    artifact_hash: str,
    config_hash: str,
    tool_version: str,
    kind: str,
) -> str:
    raw = f"{kind}|{artifact_hash}|{config_hash}|{tool_version}"
    return _sha256_text(raw)


def cache_dir() -> Path:
    override = os.environ.get("QSPECBENCH_ARTIFACT_CACHE", "").strip()
    return Path(override) if override else DEFAULT_CACHE_DIR


def cache_get(key: str) -> dict[str, Any] | None:
    path = cache_dir() / f"{key}.json"
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return payload if isinstance(payload, dict) else None


def cache_put(key: str, payload: dict[str, Any]) -> Path:
    root = cache_dir()
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{key}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def cached_compute(
    *,
    artifact_path: Path,
    kind: str,
    backend: str,
    config: dict[str, Any] | None,
    version: str | None,
    compute: Callable[[], dict[str, Any]],
    use_cache: bool = True,
) -> dict[str, Any]:
    """Return cached payload or compute and store."""
    art = artifact_sha256(artifact_path)
    cfg = config_sha256(config)
    tool = tool_version_token(backend, version)
    key = cache_key(artifact_hash=art, config_hash=cfg, tool_version=tool, kind=kind)
    if use_cache:
        hit = cache_get(key)
        if hit is not None:
            hit = dict(hit)
            hit["_cache"] = "hit"
            hit["_cache_key"] = key
            return hit
    payload = compute()
    payload = dict(payload)
    payload["_cache_key"] = key
    payload["_cache_meta"] = {
        "artifact_sha256": art,
        "config_sha256": cfg,
        "tool_version": tool,
        "kind": kind,
    }
    if use_cache:
        cache_put(key, payload)
        payload["_cache"] = "miss"
    else:
        payload["_cache"] = "bypass"
    return payload

"""Registered semantic profiles as executable, hashed contracts."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from qspecbench.schema import REPO_ROOT

PROFILES_DIR = REPO_ROOT / "schema" / "profiles"

# Parser-subset version is intentionally distinct from the upstream OpenQASM standard.
PARSER_SUBSET_VERSION = "qspecbench-openqasm-fragment-0.1"

# Canonical gate atoms interpreted by the Python matrix extractor (subset parser).
QASM_MATRIX_GATE_ATOMS: frozenset[str] = frozenset(
    {"h", "x", "y", "z", "s", "t", "sdg", "tdg", "cx", "cnot", "cz", "swap", "ccx"}
)

# Lean OpenQASM fragment atoms used by the normalized Clifford+T bridge.
LEAN_NORMALIZED_CLIFFORD_T_GATES: frozenset[str] = frozenset({"h", "t", "tdg", "cx", "ccx"})

# Lean unitary fragment additionally interprets these atoms on the Python/legacy path.
LEAN_UNITARY_FRAGMENT_GATES: frozenset[str] = LEAN_NORMALIZED_CLIFFORD_T_GATES | frozenset(
    {"i", "x", "y", "z", "s", "sdg", "rx", "swap"}
)


class ProfileError(ValueError):
    """Raised when a semantic profile cannot be resolved fail-closed."""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_profile_bytes(path: Path) -> bytes:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def profile_content_sha256(path: Path) -> str:
    return _sha256_bytes(canonical_profile_bytes(path))


@lru_cache(maxsize=64)
def load_registered_profile(profile_id: str) -> dict[str, Any]:
    path = PROFILES_DIR / f"{profile_id}.json"
    if not path.is_file():
        raise ProfileError(f"unregistered semantic profile {profile_id!r}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProfileError(f"semantic profile {profile_id!r} is unreadable: {exc}") from exc
    if payload.get("id") != profile_id:
        raise ProfileError(
            f"semantic profile id mismatch: file {profile_id!r} declares {payload.get('id')!r}"
        )
    payload["_path"] = str(path)
    payload["_content_sha256"] = profile_content_sha256(path)
    payload["_content_version"] = str(
        payload.get("profile_version") or payload.get("parser_version") or "1"
    )
    return payload


def resolve_profile_binding(
    profile_id: str,
    *,
    content_sha256: str | None = None,
    content_version: str | None = None,
) -> dict[str, Any]:
    """Resolve a registered profile and fail closed on digest/version mismatch."""
    profile = load_registered_profile(profile_id)
    if content_sha256 and content_sha256 != profile["_content_sha256"]:
        raise ProfileError(
            f"semantic profile digest mismatch for {profile_id}: "
            f"request={content_sha256} registry={profile['_content_sha256']}"
        )
    if content_version and content_version != profile["_content_version"]:
        raise ProfileError(
            f"semantic profile version mismatch for {profile_id}: "
            f"request={content_version} registry={profile['_content_version']}"
        )
    return profile


def openqasm_honesty_errors(profile: dict[str, Any]) -> list[str]:
    """The subset parser is not OpenQASM 3. Include remains skipped unless a new profile says otherwise."""
    errors: list[str] = []
    profile_id = str(profile.get("id") or "")
    if not profile_id.startswith("qspecbench.openqasm3."):
        return errors
    upstream = profile.get("upstream_standard")
    if upstream != "OpenQASM":
        errors.append(f"{profile_id}: upstream_standard must remain OpenQASM, not a parser name")
    parser_version = str(profile.get("parser_version") or "")
    upstream_version = str(profile.get("upstream_version") or "")
    if parser_version and parser_version == upstream_version:
        errors.append(
            f"{profile_id}: parser_version must not be identical to upstream_version; "
            "the subset parser is not the OpenQASM standard"
        )
    include_policy = profile.get("include_policy")
    if include_policy not in {"skipped_not_interpreted", "rejected", "declared_allowlist"}:
        errors.append(f"{profile_id}: include_policy must be explicit")
    if include_policy == "declared_allowlist":
        errors.append(
            f"{profile_id}: declared_allowlist include interpretation requires a new profile "
            "version with new evidence; current corpus profiles skip includes"
        )
    return errors


def cross_consistency_errors(profile: dict[str, Any]) -> list[str]:
    """Gate-set / wire-order / phase-policy must not silently disagree with parsers."""
    errors: list[str] = []
    profile_id = str(profile.get("id") or "")
    if not profile_id.startswith("qspecbench.openqasm3."):
        return errors
    gates = {str(g).lower() for g in profile.get("gate_set") or []}
    unknown = sorted(gates - QASM_MATRIX_GATE_ATOMS - {"i", "rx", "cnot"})
    # RX is a declared legacy surface; cnot is an alias of cx.
    _ = unknown  # unknown relative to the Python extractor is reported below per profile family
    if profile_id.endswith("clifford_t_normalized.v1"):
        if gates != LEAN_NORMALIZED_CLIFFORD_T_GATES:
            errors.append(
                f"{profile_id}: gate_set {sorted(gates)} must equal Lean normalized Clifford+T "
                f"{sorted(LEAN_NORMALIZED_CLIFFORD_T_GATES)}"
            )
        if profile.get("wire_order_convention") != "openqasm_little_endian_wire_order":
            errors.append(f"{profile_id}: wire_order must be openqasm_little_endian_wire_order")
        if profile.get("global_phase_policy") != "exact":
            errors.append(f"{profile_id}: global_phase_policy must be exact")
        if profile.get("include_policy") != "skipped_not_interpreted":
            errors.append(f"{profile_id}: include_policy must remain skipped_not_interpreted")
    if profile_id.endswith("unitary.v1"):
        extra = gates - LEAN_UNITARY_FRAGMENT_GATES
        if extra:
            errors.append(f"{profile_id}: gate_set contains atoms outside the Lean/Python fragment: {sorted(extra)}")
        if profile.get("include_policy") != "skipped_not_interpreted":
            errors.append(f"{profile_id}: include_policy must remain skipped_not_interpreted")
    errors.extend(openqasm_honesty_errors(profile))
    return errors


def graph_profile_binding(graph: dict[str, Any]) -> dict[str, str]:
    profile = graph.get("semantic_profile") or {}
    profile_id = str(profile.get("id") or "")
    resolved = resolve_profile_binding(
        profile_id,
        content_sha256=profile.get("content_sha256") or profile.get("sha256"),
        content_version=profile.get("content_version") or profile.get("profile_version"),
    )
    return {
        "id": profile_id,
        "content_sha256": resolved["_content_sha256"],
        "content_version": resolved["_content_version"],
    }


def all_registered_profile_ids() -> tuple[str, ...]:
    return tuple(sorted(path.stem for path in PROFILES_DIR.glob("*.json")))

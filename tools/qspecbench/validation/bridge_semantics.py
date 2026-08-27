"""Cross-check semantic-bridge conventions against the authoritative profile.

The bridge verifier establishes evidence-specific links. This validator establishes a
separate authority invariant: once a benchmark chooses one registered semantic
profile, bridge metadata must not silently use a different wire order or phase rule.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from qspecbench.semantic_profiles import (
    ProfileError,
    load_registered_profile,
    profile_global_phase_policy,
    profile_wire_order_convention,
)
from qspecbench.validation.semantic_authority import PROMOTED_MATURITIES

_EXACT_PHASE_BRIDGE_VALUES = {
    "exact",
    "exact_equality_global_phase_zero",
    "exact_global_phase_zero",
}


def _load_graph_profile_id(claim_dir: Path) -> str | None:
    path = claim_dir / "assurance_graph.yaml"
    if not path.is_file():
        return None
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None
    if not isinstance(payload, dict):
        return None
    profile_id = ((payload.get("semantic_profile") or {}).get("id") or "").strip()
    return profile_id or None


def _load_bridge(spec: dict[str, Any], claim_dir: Path) -> dict[str, Any] | None:
    inline = spec.get("semantic_bridge")
    if isinstance(inline, dict):
        return inline
    path = claim_dir / "expected" / "semantic_bridge.json"
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _authoritative_profile_id(spec: dict[str, Any], claim_dir: Path) -> str | None:
    spec_profile = spec.get("openqasm_profile")
    graph_profile = _load_graph_profile_id(claim_dir)
    ids = {str(value) for value in (spec_profile, graph_profile) if value}
    # Identity disagreement is reported by semantic_authority; avoid a second,
    # arbitrarily chosen authority here.
    return next(iter(ids)) if len(ids) == 1 else None


def _phase_matches(expected: str, declared: str) -> bool:
    if expected == "exact":
        return declared in _EXACT_PHASE_BRIDGE_VALUES
    return declared == expected


def validate_bridge_profile_consistency(
    spec: dict[str, Any],
    claim_dir: Path,
) -> tuple[list[str], list[str]]:
    """Validate wire-order and phase agreement between profile and bridge metadata."""
    errors: list[str] = []
    warnings: list[str] = []
    bridge = _load_bridge(spec, claim_dir)
    profile_id = _authoritative_profile_id(spec, claim_dir)
    if bridge is None or profile_id is None:
        return errors, warnings

    try:
        profile = load_registered_profile(profile_id)
    except ProfileError:
        # Dedicated profile validators own the missing/unreadable-profile error.
        return errors, warnings

    maturity = str((spec.get("status") or {}).get("maturity") or "")
    promoted = maturity in PROMOTED_MATURITIES

    expected_wire = profile_wire_order_convention(profile)
    declared_wire = ((bridge.get("wire_order") or {}).get("model") or "").strip()
    if expected_wire and declared_wire and declared_wire != expected_wire:
        message = (
            "semantic bridge/profile wire-order mismatch: "
            f"profile {profile_id!r} requires {expected_wire!r}, "
            f"bridge declares {declared_wire!r}"
        )
        (errors if promoted else warnings).append(message)

    expected_phase = profile_global_phase_policy(profile)
    normalization = bridge.get("normalization") or {}
    declared_phase = str(normalization.get("phase_policy") or "").strip()
    if expected_phase and promoted and not declared_phase:
        errors.append(
            "promoted unitary semantic bridge must declare normalization.phase_policy "
            f"consistent with profile {profile_id!r} ({expected_phase!r})"
        )
    elif expected_phase and declared_phase and not _phase_matches(expected_phase, declared_phase):
        message = (
            "semantic bridge/profile global-phase mismatch: "
            f"profile {profile_id!r} requires {expected_phase!r}, "
            f"bridge normalization.phase_policy declares {declared_phase!r}"
        )
        (errors if promoted else warnings).append(message)

    return errors, warnings

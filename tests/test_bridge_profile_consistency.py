"""Cross-layer tests for semantic profile and bridge agreement."""

from __future__ import annotations

from pathlib import Path

import yaml

from qspecbench.schema import REPO_ROOT
from qspecbench.semantic_profiles import CANONICAL_LSB_UNITARY_PROFILE
from qspecbench.validation.bridge_semantics import validate_bridge_profile_consistency


def _bridge(*, wire_order: str, phase_policy: str | None = "exact") -> dict:
    normalization = {}
    if phase_policy is not None:
        normalization["phase_policy"] = phase_policy
    return {
        "wire_order": {
            "model": wire_order,
            "checked_against": "both",
        },
        "normalization": normalization,
    }


def _spec(*, maturity: str, bridge: dict) -> dict:
    return {
        "status": {"maturity": maturity},
        "openqasm_profile": CANONICAL_LSB_UNITARY_PROFILE,
        "semantic_bridge": bridge,
    }


def test_promoted_bridge_rejects_wire_order_contradiction(tmp_path: Path) -> None:
    spec = _spec(
        maturity="reference_claim",
        bridge=_bridge(wire_order="legacy_kron_order"),
    )
    errors, warnings = validate_bridge_profile_consistency(spec, tmp_path)
    assert any("wire-order mismatch" in error for error in errors)
    assert warnings == []


def test_promoted_bridge_rejects_phase_contradiction(tmp_path: Path) -> None:
    spec = _spec(
        maturity="artifact_bound_reference_claim",
        bridge=_bridge(
            wire_order="openqasm_little_endian_wire_order",
            phase_policy="up_to_global_phase",
        ),
    )
    errors, _ = validate_bridge_profile_consistency(spec, tmp_path)
    assert any("global-phase mismatch" in error for error in errors)


def test_promoted_exact_profile_requires_explicit_bridge_phase_policy(tmp_path: Path) -> None:
    spec = _spec(
        maturity="reference_claim",
        bridge=_bridge(
            wire_order="openqasm_little_endian_wire_order",
            phase_policy=None,
        ),
    )
    errors, _ = validate_bridge_profile_consistency(spec, tmp_path)
    assert any("must declare normalization.phase_policy" in error for error in errors)


def test_experimental_bridge_contradiction_is_warning(tmp_path: Path) -> None:
    spec = _spec(
        maturity="experimental_closed",
        bridge=_bridge(wire_order="legacy_kron_order"),
    )
    errors, warnings = validate_bridge_profile_consistency(spec, tmp_path)
    assert errors == []
    assert any("wire-order mismatch" in warning for warning in warnings)


def test_toffoli_bridge_matches_authoritative_profile() -> None:
    claim_dir = REPO_ROOT / "benchmarks" / "equivalence" / "toffoli_decomposition_equivalence"
    spec = yaml.safe_load((claim_dir / "spec.yaml").read_text(encoding="utf-8"))
    errors, warnings = validate_bridge_profile_consistency(spec, claim_dir)
    assert errors == []
    assert warnings == []

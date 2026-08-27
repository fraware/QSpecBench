"""Tests for profile identity, promotion eligibility, and executable consistency."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import yaml

from qspecbench.schema import REPO_ROOT
from qspecbench.semantic_profiles import (
    CANONICAL_LSB_UNITARY_PROFILE,
    DYNAMIC_INSTRUMENT_PROFILE_V2,
    cross_consistency_errors,
    load_registered_profile,
)
from qspecbench.validation.profile_conformance import _validate_qasm_text
from qspecbench.validation.semantic_authority import validate_semantic_authority


def _write_graph(claim_dir: Path, profile_id: str) -> None:
    claim_dir.mkdir(parents=True, exist_ok=True)
    (claim_dir / "assurance_graph.yaml").write_text(
        yaml.safe_dump({"semantic_profile": {"id": profile_id}}),
        encoding="utf-8",
    )


def test_new_executable_profiles_are_cross_consistent() -> None:
    for profile_id in (CANONICAL_LSB_UNITARY_PROFILE, DYNAMIC_INSTRUMENT_PROFILE_V2):
        profile = load_registered_profile(profile_id)
        assert cross_consistency_errors(profile) == []


def test_static_v2_requires_numeric_semantic_disclosure() -> None:
    profile = deepcopy(load_registered_profile(CANONICAL_LSB_UNITARY_PROFILE))
    profile.pop("numeric_semantics")
    errors = cross_consistency_errors(profile)
    assert any("numeric_semantics" in error for error in errors)


def test_dynamic_v2_requires_numeric_semantic_disclosure() -> None:
    profile = deepcopy(load_registered_profile(DYNAMIC_INSTRUMENT_PROFILE_V2))
    profile["interpretation"].pop("numeric_semantics")
    errors = cross_consistency_errors(profile)
    assert any("numeric_semantics" in error for error in errors)


def test_promoted_claim_rejects_legacy_ambiguous_unitary_profile(tmp_path: Path) -> None:
    _write_graph(tmp_path, "qspecbench.openqasm3.unitary.v1")
    spec = {
        "status": {"maturity": "reference_claim"},
        "openqasm_profile": "qspecbench.openqasm3.unitary.v1",
    }
    errors, warnings = validate_semantic_authority(spec, tmp_path)
    assert any("not eligible for promoted claims" in error for error in errors)
    assert warnings == []


def test_promoted_claim_rejects_spec_graph_profile_mismatch(tmp_path: Path) -> None:
    _write_graph(tmp_path, DYNAMIC_INSTRUMENT_PROFILE_V2)
    spec = {
        "status": {"maturity": "artifact_bound_reference_claim"},
        "openqasm_profile": CANONICAL_LSB_UNITARY_PROFILE,
    }
    errors, _ = validate_semantic_authority(spec, tmp_path)
    assert any("semantic authority mismatch" in error for error in errors)


def test_experimental_profile_mismatch_is_explicit_migration_warning(tmp_path: Path) -> None:
    _write_graph(tmp_path, DYNAMIC_INSTRUMENT_PROFILE_V2)
    spec = {
        "status": {"maturity": "experimental_closed"},
        "openqasm_profile": CANONICAL_LSB_UNITARY_PROFILE,
    }
    errors, warnings = validate_semantic_authority(spec, tmp_path)
    assert errors == []
    assert any("semantic authority mismatch" in warning for warning in warnings)


def test_normalized_clifford_t_profile_rejects_rx() -> None:
    profile = load_registered_profile("qspecbench.openqasm3.clifford_t_normalized.v1")
    errors = _validate_qasm_text(
        "OPENQASM 3.0;\nqubit[1] q;\nrx(pi/4) q[0];\n",
        "artifact.qasm",
        profile,
    )
    assert any("gate 'rx' is not declared" in error for error in errors)


def test_canonical_static_profile_rejects_classical_control() -> None:
    profile = load_registered_profile(CANONICAL_LSB_UNITARY_PROFILE)
    errors = _validate_qasm_text(
        "OPENQASM 3.0;\nqubit[1] q;\nif (c == 1) x q[0];\n",
        "artifact.qasm",
        profile,
    )
    assert any("classical control appears under control_flow_support=none" in error for error in errors)


def test_toffoli_is_bound_to_normalized_lsb_profile() -> None:
    claim_dir = REPO_ROOT / "benchmarks" / "equivalence" / "toffoli_decomposition_equivalence"
    spec = yaml.safe_load((claim_dir / "spec.yaml").read_text(encoding="utf-8"))
    graph = yaml.safe_load((claim_dir / "assurance_graph.yaml").read_text(encoding="utf-8"))

    expected = "qspecbench.openqasm3.clifford_t_normalized.v1"
    assert spec["openqasm_profile"] == expected
    assert graph["semantic_profile"]["id"] == expected
    assert graph["semantic_profile"]["wire_order"] == "openqasm_little_endian_wire_order"

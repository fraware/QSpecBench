# -*- coding: utf-8 -*-
"""Negative regression tests for permanent residual locks (Wave 0.1)."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
import yaml

from qspecbench.hardware_isa_adapter import (
    HardwareIsaAdapterError,
    verify_hardware_isa_abstraction,
)
from qspecbench.permanent_residuals import (
    DECLARED_STIM_UNIVERSE_ID,
    validate_hardware_isa_payload,
    validate_permanent_residual_docs,
    validate_permanent_residuals,
    validate_stim_declared_universe_payload,
)
from qspecbench.reviews import validate_review_artifact_payload
from qspecbench.trust import validate_trust_rules

REPO = Path(__file__).resolve().parents[1]
MINIMAL = REPO / "schema" / "examples" / "minimal.spec.yaml"
TOFFOLI = REPO / "benchmarks/equivalence/toffoli_decomposition_equivalence"
BITFLIP = REPO / "benchmarks/qec/three_qubit_bit_flip_code_corrects_one_x"
SIBLING = REPO / "benchmarks/algorithms/teleportation_dynamic_feedforward_protocol"


def _base() -> dict:
    spec = yaml.safe_load(MINIMAL.read_text(encoding="utf-8"))
    spec["claim_scope"] = {
        "headline_claim_id": "h",
        "headline_claim_text": "test",
        "required_obligations": ["ob_a"],
    }
    spec["proved_scope"] = {
        "checked_obligations": ["ob_a"],
        "unproved_obligations": [],
    }
    spec["headline_claim_status"] = {
        "status": "partially_checked",
        "checked_under": ["ob_a"],
        "not_checked_under": ["hardware_semantics"],
        "notes": None,
    }
    return spec


def test_unbounded_all_codes_mwpm_must_stay_not_applicable():
    spec = _base()
    spec["proof_obligations"] = [
        {"id": "unbounded_all_codes_mwpm", "status": "passing", "notes": "fake close"}
    ]
    errors = validate_permanent_residuals(spec)
    assert any("unbounded_all_codes_mwpm" in e and "not_applicable" in e for e in errors)


def test_unbounded_all_codes_mwpm_checked_obligations_rejected():
    spec = _base()
    spec["proved_scope"]["checked_obligations"] = ["ob_a", "unbounded_all_codes_mwpm"]
    errors = validate_permanent_residuals(spec)
    assert any("unbounded_all_codes_mwpm" in e and "checked_obligations" in e for e in errors)


def test_unbounded_all_codes_mwpm_honest_not_applicable_ok():
    spec = _base()
    spec["proof_obligations"] = [
        {
            "id": "unbounded_all_codes_mwpm",
            "status": "not_applicable",
            "notes": "open-ended family",
        }
    ]
    errors = validate_permanent_residuals(spec)
    assert not any("unbounded_all_codes_mwpm" in e for e in errors)


def test_device_residuals_cannot_be_checked_under():
    for oid in (
        "hardware_semantics",
        "device_fidelity",
        "pulse_schedule_semantics",
    ):
        spec = _base()
        spec["headline_claim_status"]["checked_under"] = ["ob_a", oid]
        errors = validate_permanent_residuals(spec)
        assert any(oid in e and "checked_under" in e for e in errors), oid


def test_isa_layer_cannot_satisfy_device_residuals():
    spec = _base()
    spec["proved_scope"]["checked_obligations"] = [
        "ob_a",
        "hardware_abstraction_isa_layer",
        "hardware_semantics",
    ]
    errors = validate_permanent_residuals(spec)
    assert any("ISA-layer" in e and "hardware_semantics" in e for e in errors)


def test_isa_formal_claim_cannot_support_device_residual():
    spec = _base()
    spec["formal_claims"] = [
        {
            "id": "fc_isa",
            "evidence_id": "e1",
            "formal_system": "lean",
            "theorem": "t",
            "supports": ["hardware_abstraction_isa_layer", "device_fidelity"],
            "does_not_support": [],
            "benchmark_anchor": "minimal_example",
        }
    ]
    errors = validate_permanent_residuals(spec)
    assert any("device_fidelity" in e for e in errors)


def test_hardware_isa_adapter_rejects_pulse_claim(tmp_path):
    profile = SIBLING / "artifacts/hardware_isa_profile.json"
    if not profile.is_file():
        pytest.skip("ISA profile not packaged")
    data = json.loads(profile.read_text(encoding="utf-8"))
    data["pulse_schedule_semantics_checked"] = True
    bad = tmp_path / "bad_pulse.json"
    bad.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(HardwareIsaAdapterError, match="pulse_schedule"):
        verify_hardware_isa_abstraction(bad)


def test_hardware_isa_adapter_rejects_device_obligation_list(tmp_path):
    profile = SIBLING / "artifacts/hardware_isa_profile.json"
    if not profile.is_file():
        pytest.skip("ISA profile not packaged")
    data = json.loads(profile.read_text(encoding="utf-8"))
    data["satisfied_obligations"] = ["hardware_semantics"]
    bad = tmp_path / "bad_sat.json"
    bad.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(HardwareIsaAdapterError, match="hardware_semantics"):
        verify_hardware_isa_abstraction(bad)


def test_hardware_isa_result_never_claims_device_or_pulse():
    profile = SIBLING / "artifacts/hardware_isa_profile.json"
    if not profile.is_file():
        pytest.skip("ISA profile not packaged")
    result = verify_hardware_isa_abstraction(profile)
    assert result["hardware_semantics_checked"] is False
    assert result["pulse_schedule_semantics_checked"] is False
    assert result["claims_device_fidelity"] is False
    assert result["claims_pulse_schedule_semantics"] is False
    assert "hardware_abstraction_isa_layer" in result["satisfied_obligations"]
    assert not (
        set(result["satisfied_obligations"])
        & {"hardware_semantics", "device_fidelity", "pulse_schedule_semantics"}
    )
    assert validate_hardware_isa_payload(result) == []


def test_hardware_isa_payload_validator_rejects_fake_device_claim():
    errors = validate_hardware_isa_payload(
        {
            "ok": True,
            "hardware_semantics_checked": True,
            "claims_device_fidelity": False,
            "pulse_schedule_semantics_checked": False,
        }
    )
    assert any("hardware_semantics_checked" in e for e in errors)


def test_unnormalized_toffoli_cannot_be_promoted_checked():
    spec = yaml.safe_load((TOFFOLI / "spec.yaml").read_text(encoding="utf-8"))
    # Honest corpus must already keep unnormalized out of checked scope.
    assert "unnormalized_denotateOps3C_pair_equality" not in (
        spec.get("proved_scope") or {}
    ).get("checked_obligations", [])
    assert "unnormalized_denotateOps3C_pair_equality" in (
        spec.get("headline_claim_status") or {}
    ).get("not_checked_under", [])

    forged = copy.deepcopy(spec)
    forged["proved_scope"]["checked_obligations"] = list(
        forged["proved_scope"]["checked_obligations"]
    ) + ["unnormalized_denotateOps3C_pair_equality"]
    forged["headline_claim_status"]["checked_under"] = list(
        forged["headline_claim_status"]["checked_under"]
    ) + ["unnormalized_denotateOps3C_pair_equality"]
    errors = validate_trust_rules(forged, TOFFOLI)
    assert any("unnormalized_denotateOps3C_pair_equality" in e for e in errors)


def test_unnormalized_toffoli_formal_support_rejected():
    spec = _base()
    spec["formal_claims"] = [
        {
            "id": "fc_bad",
            "evidence_id": "e1",
            "formal_system": "lean",
            "theorem": "t",
            "supports": ["unnormalized_denotateOps3C_pair_equality"],
            "does_not_support": [],
            "benchmark_anchor": "minimal_example",
        }
    ]
    errors = validate_permanent_residuals(spec)
    assert any("unnormalized_denotateOps3C_pair_equality" in e for e in errors)


def test_stim_declared_universe_cannot_rename_as_unbounded():
    errors = validate_stim_declared_universe_payload(
        {
            "ok": True,
            "universe_id": "stim_all_codes_industrial",
            "unbounded_all_codes_mwpm": False,
            "unbounded_all_codes_mwpm_status": "not_applicable",
        }
    )
    assert any("universe_id" in e or "rename" in e for e in errors)


def test_stim_declared_universe_cannot_set_unbounded_true():
    errors = validate_stim_declared_universe_payload(
        {
            "ok": True,
            "universe_id": DECLARED_STIM_UNIVERSE_ID,
            "unbounded_all_codes_mwpm": True,
            "unbounded_all_codes_mwpm_status": "not_applicable",
        }
    )
    assert any("unbounded_all_codes_mwpm=true" in e for e in errors)


def test_stim_declared_universe_status_must_be_not_applicable():
    errors = validate_stim_declared_universe_payload(
        {
            "ok": True,
            "universe_id": DECLARED_STIM_UNIVERSE_ID,
            "unbounded_all_codes_mwpm": False,
            "unbounded_all_codes_mwpm_status": "passing",
        }
    )
    assert any("not_applicable" in e for e in errors)


def test_stim_forbidden_checked_label_rejected():
    spec = _base()
    spec["headline_claim_status"]["checked_under"] = [
        "ob_a",
        "industrial_all_codes_stim",
    ]
    errors = validate_permanent_residuals(spec)
    assert any("industrial_all_codes_stim" in e for e in errors)


def test_bitflip_corpus_keeps_unbounded_not_applicable():
    spec = yaml.safe_load((BITFLIP / "spec.yaml").read_text(encoding="utf-8"))
    errors = validate_trust_rules(spec, BITFLIP)
    assert not any("unbounded_all_codes_mwpm" in e for e in errors)
    status = None
    for entry in spec.get("proof_obligations") or []:
        if entry.get("id") == "unbounded_all_codes_mwpm":
            status = entry.get("status")
    assert status == "not_applicable"


def test_review_cannot_accept_permanent_residual():
    payload = {
        "benchmark_id": "minimal_example",
        "commit_sha": "a" * 40,
        "reviewer": "alice-formal",
        "reviewer_role": "formal_evidence",
        "reviewed_artifacts": ["spec.yaml"],
        "commands_executed": ["qspecbench validate"],
        "accepted_obligations": ["hardware_semantics"],
        "rejected_obligations": [],
        "residual_assumptions": [],
        "conflict_of_interest": {"is_author": False, "is_merging_maintainer": False},
        "decision": "approved",
        "signature": "test-sig",
        "proposition_id": "minimal_example_v1",
    }
    spec = _base()
    spec["id"] = "minimal_example"
    errors = validate_review_artifact_payload(
        payload,
        spec=spec,
        axis_key="formal_evidence_review",
        reviewer="alice-formal",
        review_commit="a" * 40,
        authorship={"author": "bob", "merging_maintainer": "carol"},
        label="reference_claim",
        rel="reviews/formal_review.json",
    )
    assert any("hardware_semantics" in e and "accepted_obligations" in e for e in errors)


def test_permanent_residual_doc_drift_guard():
    errors = validate_permanent_residual_docs(REPO)
    assert errors == [], "doc drift:\n" + "\n".join(errors)


def test_trust_rules_wire_permanent_residuals():
    spec = _base()
    spec["proof_obligations"] = [
        {"id": "unbounded_all_codes_mwpm", "status": "partial", "notes": "bad"}
    ]
    errors = validate_trust_rules(spec)
    assert any("unbounded_all_codes_mwpm" in e for e in errors)

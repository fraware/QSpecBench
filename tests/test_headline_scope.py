"""Tests for scoped maturity, headline obligations, and evidence-type discipline."""

from __future__ import annotations

from pathlib import Path

import yaml

from qspecbench.trust import validate_trust_rules

REPO = Path(__file__).resolve().parents[1]
MINIMAL = REPO / "schema" / "examples" / "minimal.spec.yaml"


def _base() -> dict:
    spec = yaml.safe_load(MINIMAL.read_text(encoding="utf-8"))
    spec["claim_scope"] = {
        "headline_claim_id": "minimal_headline",
        "headline_claim_text": spec["informal_claim"]["statement"],
        "required_obligations": ["headline_claim"],
    }
    spec["proved_scope"] = {
        "checked_obligations": [],
        "unproved_obligations": ["headline_claim", "artifact_parsing", "idealized_gate_semantics"],
    }
    spec["headline_claim_status"] = {"status": "unproved", "notes": None}
    return spec


def _checked_lean_evidence() -> dict:
    return {
        "id": "lean_obligation",
        "type": "lean_proof",
        "path": "evidence/proof.lean",
        "checker": "Lean 4 kernel",
        "status": "passing",
    }


def _formal_claim_for_lean() -> dict:
    return {
        "id": "formal_lean_obligation",
        "evidence_id": "lean_obligation",
        "formal_system": "lean",
        "module": "QSpecBench.Example",
        "theorem": "example_theorem",
        "supports": ["headline_claim"],
        "does_not_support": [],
        "benchmark_anchor": "minimal_example",
    }


def test_scaffold_requires_checked_evidence():
    spec = _base()
    spec["status"]["maturity"] = "reference_scaffold"
    spec["evidence"] = []
    errors = validate_trust_rules(spec)
    assert any("at least one passing checked evidence" in e for e in errors)


def test_scaffold_with_checked_evidence_ok():
    spec = _base()
    spec["status"]["maturity"] = "reference_scaffold"
    spec["evidence"] = [_checked_lean_evidence()]
    spec["formal_claims"] = [_formal_claim_for_lean()]
    spec["proved_scope"]["checked_obligations"] = ["headline_claim"]
    errors = validate_trust_rules(spec)
    assert not errors, errors


def test_scaffold_cannot_claim_checked_headline():
    spec = _base()
    spec["status"]["maturity"] = "reference_scaffold"
    spec["evidence"] = [_checked_lean_evidence()]
    spec["headline_claim_status"] = {"status": "checked", "notes": None}
    errors = validate_trust_rules(spec)
    assert any("cannot declare headline_claim_status checked" in e for e in errors)


def test_undeclared_evidence_type_rejected():
    spec = _base()
    spec["status"]["maturity"] = "usable"
    spec["evidence"] = [
        {
            "id": "stray_sim",
            "type": "simulation",
            "path": "evidence/sim.json",
            "checker": "numpy",
            "status": "partial",
        }
    ]
    errors = validate_trust_rules(spec)
    assert any("not declared in acceptable_evidence" in e for e in errors)


def _reference_claim_spec() -> dict:
    spec = _base()
    spec["status"]["maturity"] = "reference_claim"
    spec["acceptable_evidence"] = [
        {
            "type": "lean_proof",
            "checker": "Lean 4 kernel",
            "path": None,
            "required_for_claim": True,
            "trust_level": "checked",
        }
    ]
    spec["evidence"] = [_checked_lean_evidence()]
    spec["claim_scope"] = {
        "headline_claim_id": "h",
        "headline_claim_text": "Everything required is proved.",
        "required_obligations": ["ob_a"],
    }
    spec["proved_scope"] = {
        "checked_obligations": ["ob_a"],
        "unproved_obligations": [],
    }
    spec["headline_claim_status"] = {"status": "checked", "notes": None}
    spec["formal_claims"] = [_formal_claim_for_lean()]
    return spec


def test_reference_claim_fully_checked_ok():
    spec = _reference_claim_spec()
    errors = validate_trust_rules(spec)
    assert not errors, errors


def test_reference_claim_with_unchecked_obligation_rejected():
    spec = _reference_claim_spec()
    spec["claim_scope"]["required_obligations"] = ["ob_a", "ob_b"]
    errors = validate_trust_rules(spec)
    assert any("unchecked headline obligations" in e for e in errors)


def test_reference_claim_not_checked_status_rejected():
    spec = _reference_claim_spec()
    spec["headline_claim_status"]["status"] = "partially_checked"
    errors = validate_trust_rules(spec)
    assert any("headline_claim_status.status == checked" in e for e in errors)


def test_reference_claim_requires_passing_required_evidence():
    spec = _reference_claim_spec()
    # Required lean evidence is now only partial -> not passing.
    spec["evidence"] = [dict(_checked_lean_evidence(), status="partial")]
    errors = validate_trust_rules(spec)
    assert any("required_for_claim type" in e for e in errors)

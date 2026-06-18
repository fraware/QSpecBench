"""Trust boundary rule tests."""

import copy

import yaml
from qspecbench.trust import validate_trust_rules

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_ai_draft_must_be_untrusted():
    spec = yaml.safe_load((REPO / "schema/examples/minimal.spec.yaml").read_text(encoding="utf-8"))
    spec["acceptable_evidence"].append({
        "type": "ai_draft",
        "checker": "none",
        "path": None,
        "required_for_claim": False,
        "trust_level": "checked",
    })
    errors = validate_trust_rules(spec)
    assert any("ai_draft" in e for e in errors)


def test_simulation_cannot_be_checked_acceptable():
    spec = yaml.safe_load((REPO / "schema/examples/minimal.spec.yaml").read_text(encoding="utf-8"))
    spec["acceptable_evidence"].append({
        "type": "simulation",
        "checker": "sim",
        "path": None,
        "required_for_claim": False,
        "trust_level": "checked",
    })
    errors = validate_trust_rules(spec)
    assert any("simulation" in e for e in errors)


def test_reference_requires_checked_passing_evidence():
    spec = yaml.safe_load((REPO / "schema/examples/minimal.spec.yaml").read_text(encoding="utf-8"))
    spec["status"] = {
        "informal_claim": "complete",
        "machine_spec": "complete",
        "artifacts": "complete",
        "evidence": "partial",
        "ci": "passing",
        "maturity": "reference",
    }
    spec["evidence"] = [
        {
            "id": "review_only",
            "type": "human_review",
            "path": "notes/informal_derivation.md",
            "checker": "reviewer",
            "status": "partial",
        }
    ]
    errors = validate_trust_rules(spec)
    assert any("reference maturity" in e for e in errors)


def test_ai_draft_passing_evidence_rejected():
    spec = yaml.safe_load((REPO / "schema/examples/minimal.spec.yaml").read_text(encoding="utf-8"))
    spec["evidence"] = [
        {
            "id": "bad_draft",
            "type": "ai_draft",
            "path": "artifacts/draft.lean",
            "checker": "none",
            "status": "passing",
        }
    ]
    errors = validate_trust_rules(spec)
    assert any("ai_draft cannot be passing" in e for e in errors)

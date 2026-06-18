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

"""Tests for claim_diff freshness validation."""

from __future__ import annotations

from pathlib import Path

import yaml

from qspecbench.claim_diff import (
    claim_diff_fingerprint,
    claim_diff_report,
    claim_diff_scope_payload,
    validate_claim_diff,
)

REPO = Path(__file__).resolve().parents[1]


def test_claim_diff_fingerprint_changes_when_scope_changes():
    spec_path = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation/spec.yaml"
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    fp1 = claim_diff_fingerprint(spec)
    spec["proved_scope"]["unproved_obligations"] = list(
        spec["proved_scope"]["unproved_obligations"]
    ) + ["extra_obligation"]
    fp2 = claim_diff_fingerprint(spec)
    assert fp1 != fp2


def test_claim_diff_fingerprint_changes_when_informal_claim_changes():
    spec_path = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation/spec.yaml"
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    fp1 = claim_diff_fingerprint(spec)
    spec["informal_claim"] = dict(spec.get("informal_claim") or {})
    spec["informal_claim"]["statement"] = (spec["informal_claim"].get("statement") or "") + " extra"
    fp2 = claim_diff_fingerprint(spec)
    assert fp1 != fp2


def test_claim_diff_fingerprint_changes_when_maturity_changes():
    spec_path = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation/spec.yaml"
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    fp1 = claim_diff_fingerprint(spec)
    spec["status"] = dict(spec.get("status") or {})
    spec["status"]["maturity"] = "reference_scaffold"
    fp2 = claim_diff_fingerprint(spec)
    assert fp1 != fp2


def test_claim_diff_scope_payload_includes_informal_claim_and_maturity():
    spec = {
        "informal_claim": {"statement": "test"},
        "status": {"maturity": "reference_scaffold"},
        "claim_scope": {},
        "proved_scope": {},
        "headline_claim_status": {},
    }
    payload = claim_diff_scope_payload(spec)
    assert payload["informal_claim"] == {"statement": "test"}
    assert payload["maturity"] == "reference_scaffold"


def test_stale_claim_diff_detected(tmp_path):
    claim = tmp_path / "claim"
    evidence = claim / "evidence"
    evidence.mkdir(parents=True)
    spec = {
        "id": "stale_test",
        "status": {"maturity": "reference_scaffold"},
        "informal_claim": {"statement": "test"},
        "claim_scope": {
            "headline_claim_id": "h",
            "headline_claim_text": "test",
            "required_obligations": ["a"],
        },
        "proved_scope": {"checked_obligations": [], "unproved_obligations": ["a"]},
        "headline_claim_status": {"status": "unproved"},
    }
    (claim / "spec.yaml").write_text(yaml.dump(spec), encoding="utf-8")
    (evidence / "claim_diff.md").write_text("# stale content\n", encoding="utf-8")
    errors = validate_claim_diff(claim)
    assert errors


def test_fresh_claim_diff_passes():
    claim = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation"
    spec = yaml.safe_load((claim / "spec.yaml").read_text(encoding="utf-8"))
    report = claim_diff_report(spec)
    (claim / "evidence" / "claim_diff.md").write_text(report, encoding="utf-8")
    assert not validate_claim_diff(claim)

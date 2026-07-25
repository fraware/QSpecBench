"""Phase 9 governance: review schema, CODEOWNERS, audit ledger."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import yaml

from qspecbench.reviews import validate_promotion_reviews, validate_review_artifact_payload
from qspecbench.schema import SCHEMA_DIR
from qspecbench.validate import load_spec

REPO = Path(__file__).resolve().parents[1]


def test_review_artifact_schema_validates_corpus_examples():
    schema = json.loads((SCHEMA_DIR / "review_artifact.schema.json").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    files = list((REPO / "benchmarks").rglob("reviews/*.json"))
    assert len(files) >= 10
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        validator.validate(payload)


def test_codeowners_covers_required_paths():
    text = (REPO / ".github/CODEOWNERS").read_text(encoding="utf-8")
    for needle in (
        "benchmarks/qec/**",
        "benchmarks/hamiltonian/**",
        "benchmarks/ai_formalization/**",
        "lean/**",
        "schema/**",
        "adapters/**",
    ):
        assert needle in text or needle.lstrip("/") in text or f"/{needle}" in text


def test_audit_issues_yaml_structured():
    payload = yaml.safe_load((REPO / "docs/audit_issues.yaml").read_text(encoding="utf-8"))
    assert payload.get("version") == 1
    findings = payload.get("findings") or []
    assert len(findings) >= 20
    ids = {f["id"] for f in findings}
    assert "F-010" in ids
    f010 = next(f for f in findings if f["id"] == "F-010")
    assert f010["status"] == "closed"
    for f in findings:
        assert "severity" in f and "status" in f and "title" in f
        assert "github_issue" in f
        assert "acceptance_tests" in f
        assert "depends_on" in f


def test_review_separation_rejects_author_as_reviewer():
    claim = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation"
    spec = load_spec(claim / "spec.yaml")
    author = (spec.get("authorship") or {}).get("author")
    assert author
    spec["status"]["reviews"]["formal_evidence_review"]["reviewer"] = author
    errors = validate_promotion_reviews(spec, claim)
    assert any("cannot be the benchmark author" in e for e in errors)


def test_review_artifact_role_mismatch_rejected():
    claim = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation"
    spec = load_spec(claim / "spec.yaml")
    path = claim / "reviews/formal_review.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["reviewer_role"] = "domain_semantics"
    errors = validate_review_artifact_payload(
        payload,
        spec=spec,
        axis_key="formal_evidence_review",
        reviewer=payload["reviewer"],
        review_commit=payload["commit_sha"],
        authorship=spec.get("authorship") or {},
        label="test",
        rel="reviews/formal_review.json",
    )
    assert any("reviewer_role" in e for e in errors)

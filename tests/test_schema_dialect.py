"""Schema dialect migration and promotion-review provenance tests."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from qspecbench.reviews import validate_promotion_reviews
from qspecbench.schema_dialect import validate_schema_dialect
from qspecbench.validate import load_spec, validate_spec_dict

REPO = Path(__file__).resolve().parents[1]
EXAMPLES = REPO / "schema" / "examples"


def _minimal() -> dict:
    return yaml.safe_load((EXAMPLES / "minimal.spec.yaml").read_text(encoding="utf-8"))


def test_all_active_specs_declare_0_3():
    for path in (REPO / "benchmarks").rglob("spec.yaml"):
        if "_template" in path.parts:
            continue
        spec = load_spec(path)
        assert spec.get("qspecbench_version") == "0.3", path


def test_schema_0_2_forbids_artifact_bound_maturity():
    spec = _minimal()
    spec["qspecbench_version"] = "0.2"
    spec.setdefault("status", {})["maturity"] = "artifact_bound_reference_claim"
    errors = validate_schema_dialect(spec)
    assert any("0.2 forbids maturity artifact_bound_reference_claim" in e for e in errors)


def test_schema_0_1_forbids_claim_scope():
    spec = _minimal()
    spec["qspecbench_version"] = "0.1"
    spec["claim_scope"] = {
        "headline_claim_id": "x",
        "headline_claim_text": "t",
        "required_obligations": ["a"],
    }
    errors = validate_schema_dialect(spec)
    assert any("0.1 forbids field 'claim_scope'" in e for e in errors)


def test_schema_0_2_forbids_elaborator_hash_inline():
    spec = _minimal()
    spec["qspecbench_version"] = "0.2"
    spec["semantic_bridge"] = {
        "artifact_gate_model": "openqasm3_1q2q_clifford",
        "lean_module": "M",
        "lean_theorem": "t",
        "normalization": {},
        "claimed_link": "documented_not_proved",
        "wire_order": {"model": "legacy_kron_order", "checked_against": "lean"},
        "theorem_elaborator_hash": "a" * 64,
    }
    errors = validate_schema_dialect(spec)
    assert any("theorem_elaborator_hash" in e for e in errors)


def test_schema_0_3_allows_artifact_bound_maturity_dialect():
    spec = _minimal()
    spec["qspecbench_version"] = "0.3"
    spec.setdefault("status", {})["maturity"] = "artifact_bound_reference_claim"
    assert validate_schema_dialect(spec) == []


def test_maintainer_bootstrap_rejected_for_checked_headline(tmp_path):
    claim = tmp_path / "bench"
    (claim / "reviews").mkdir(parents=True)
    spec = {
        "id": "bench",
        "status": {
            "maturity": "reference_claim",
            "reviews": {
                "formal_evidence_review": {
                    "status": "approved",
                    "reviewer": "maintainer-bootstrap",
                    "review_artifact_path": "reviews/formal_review.json",
                    "review_artifact_sha256": "0" * 64,
                    "review_commit": "abc",
                },
                "domain_semantics_review": {
                    "status": "approved",
                    "reviewer": "mlewis-quant-sem",
                    "review_artifact_path": "reviews/domain_review.json",
                    "review_artifact_sha256": "0" * 64,
                    "review_commit": "abc",
                },
            },
        },
        "headline_claim_status": {"status": "checked"},
        "authorship": {"author": "fraware", "merging_maintainer": "fraware"},
    }
    for name in ("formal_review.json", "domain_review.json"):
        (claim / "reviews" / name).write_text("{}", encoding="utf-8")
    errors = validate_promotion_reviews(spec, claim)
    assert any("maintainer-bootstrap" in e for e in errors)


def test_required_review_status_rejected(tmp_path):
    claim = tmp_path / "bench"
    claim.mkdir()
    spec = {
        "status": {
            "maturity": "reference_claim",
            "reviews": {
                "formal_evidence_review": {
                    "status": "required",
                    "reviewer": "rkothari-formal",
                },
                "domain_semantics_review": {
                    "status": "approved",
                    "reviewer": "mlewis-quant-sem",
                },
            },
        },
        "headline_claim_status": {"status": "checked"},
    }
    errors = validate_promotion_reviews(spec, claim)
    assert any("'required' is not a completed promotion status" in e for e in errors)


def test_same_reviewer_both_axes_rejected(tmp_path):
    claim = tmp_path / "bench"
    (claim / "reviews").mkdir(parents=True)
    payload = {
        "reviewer": "rkothari-formal",
        "decision": "approved",
    }
    for name in ("formal_review.json", "domain_review.json"):
        path = claim / "reviews" / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
    spec = {
        "id": "bench",
        "status": {
            "maturity": "reference_claim",
            "reviews": {
                "formal_evidence_review": {
                    "status": "approved",
                    "reviewer": "rkothari-formal",
                    "review_artifact_path": "reviews/formal_review.json",
                    "review_artifact_sha256": digest,
                    "review_commit": "abc",
                },
                "domain_semantics_review": {
                    "status": "approved",
                    "reviewer": "rkothari-formal",
                    "review_artifact_path": "reviews/domain_review.json",
                    "review_artifact_sha256": digest,
                    "review_commit": "abc",
                },
            },
        },
        "headline_claim_status": {"status": "checked"},
        "authorship": {"author": "fraware", "merging_maintainer": "fraware"},
    }
    errors = validate_promotion_reviews(spec, claim)
    assert any("distinct formal and domain reviewers" in e for e in errors)


def test_review_hash_drift_rejected(tmp_path):
    claim = tmp_path / "bench"
    (claim / "reviews").mkdir(parents=True)
    path = claim / "reviews" / "formal_review.json"
    path.write_text(json.dumps({"reviewer": "rkothari-formal", "decision": "approved"}), encoding="utf-8")
    domain = claim / "reviews" / "domain_review.json"
    domain.write_text(json.dumps({"reviewer": "mlewis-quant-sem", "decision": "approved"}), encoding="utf-8")
    domain_digest = hashlib.sha256(domain.read_bytes()).hexdigest()
    spec = {
        "id": "bench",
        "status": {
            "maturity": "reference_claim",
            "reviews": {
                "formal_evidence_review": {
                    "status": "approved",
                    "reviewer": "rkothari-formal",
                    "review_artifact_path": "reviews/formal_review.json",
                    "review_artifact_sha256": "a" * 64,
                    "review_commit": "abc",
                },
                "domain_semantics_review": {
                    "status": "approved",
                    "reviewer": "mlewis-quant-sem",
                    "review_artifact_path": "reviews/domain_review.json",
                    "review_artifact_sha256": domain_digest,
                    "review_commit": "abc",
                },
            },
        },
        "headline_claim_status": {"status": "checked"},
        "authorship": {"author": "fraware", "merging_maintainer": "fraware"},
    }
    errors = validate_promotion_reviews(spec, claim)
    assert any("review_artifact_sha256 drift" in e for e in errors)


def test_role_alias_reviewer_rejected(tmp_path):
    claim = tmp_path / "bench"
    claim.mkdir()
    spec = {
        "status": {
            "maturity": "artifact_bound_reference_claim",
            "reviews": {
                "formal_evidence_review": {
                    "status": "approved",
                    "reviewer": "qspecbench-formal-reviewer",
                },
                "domain_semantics_review": {
                    "status": "approved",
                    "reviewer": "qspecbench-domain-reviewer",
                },
            },
        },
        "headline_claim_status": {"status": "checked"},
    }
    errors = validate_promotion_reviews(spec, claim)
    assert any("forbidden bootstrap/role alias" in e for e in errors)


def test_native_ccx_and_toffoli_split_claims():
    native = load_spec(
        REPO / "benchmarks/equivalence/native_ccx_artifact_denotes_toffoli_unitary/spec.yaml"
    )
    decomp = load_spec(
        REPO / "benchmarks/equivalence/toffoli_decomposition_equivalence/spec.yaml"
    )
    claim = (
        "The declared native CCX artifact denotes the standard three-qubit Toffoli "
        "unitary under the declared finite matrix semantics."
    )
    assert native["status"]["maturity"] == "artifact_bound_reference_claim"
    assert " ".join(native["informal_claim"]["statement"].split()) == claim
    assert " ".join(native["claim_scope"]["headline_claim_text"].split()) == claim
    assert decomp["status"]["maturity"] == "artifact_bound_reference_claim"
    assert decomp["headline_claim_status"]["status"] == "checked"
    assert "normalized Clifford+T" in decomp["informal_claim"]["statement"]
    assert decomp["proved_scope"]["unproved_obligations"] == []
    assert (
        decomp["claim_identity"]["proposition_id"]
        == "toffoli_decomposition_equivalence_v1"
    )

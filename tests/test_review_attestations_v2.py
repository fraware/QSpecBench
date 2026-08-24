import hashlib
import json
from pathlib import Path

from qspecbench.validation.review_attestations import validate_review_attestations


def _setup(tmp_path: Path) -> tuple[Path, dict, dict]:
    schema_dir = tmp_path / "schema"
    schema_dir.mkdir()
    schema_dir.joinpath("review_attestation_v2.schema.json").write_text(
        Path("schema/review_attestation_v2.schema.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    claim_dir = tmp_path / "benchmarks" / "equivalence" / "demo"
    claim_dir.mkdir(parents=True)
    artifact = claim_dir / "proof.lean"
    artifact.write_text("theorem demo : True := by trivial\n", encoding="utf-8")
    graph = {
        "proposition": {"id": "demo_v1"},
        "obligations": [{"id": "equivalence", "required": True}],
        "review_attestations": ["reviews/formal.json", "reviews/domain.json"],
    }
    spec = {
        "id": "demo",
        "status": {"maturity": "reference_claim"},
        "authorship": {"author": "author", "merging_maintainer": "merger"},
    }
    (claim_dir / "reviews").mkdir()
    return claim_dir, graph, spec


def _attestation(claim_dir: Path, login: str, user_id: int, role: str) -> dict:
    artifact = claim_dir / "proof.lean"
    sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
    return {
        "schema": "qspecbench.review_attestation.v2",
        "benchmark_id": "demo",
        "proposition_id": "demo_v1",
        "reviewer": {
            "name": login,
            "github_login": login,
            "github_user_id": user_id,
            "orcid": None,
        },
        "role": role,
        "reviewed_commit": "a" * 40,
        "public_review": {"pull_request": 11, "review_id": 100 + user_id, "url": None},
        "reviewed_artifacts": [{"path": "proof.lean", "sha256": sha}],
        "accepted_obligations": ["equivalence"],
        "rejected_obligations": [],
        "residual_assumptions": [],
        "conflicts": [],
        "decision": "approved",
        "attestation": {"method": "github_review", "reference": f"review-{user_id}"},
    }


def test_two_distinct_authenticated_review_roles_pass(tmp_path: Path) -> None:
    claim_dir, graph, spec = _setup(tmp_path)
    (claim_dir / "reviews/formal.json").write_text(
        json.dumps(_attestation(claim_dir, "formal-reviewer", 1, "formal_evidence")),
        encoding="utf-8",
    )
    (claim_dir / "reviews/domain.json").write_text(
        json.dumps(_attestation(claim_dir, "domain-reviewer", 2, "domain_semantics")),
        encoding="utf-8",
    )
    errors, _warnings = validate_review_attestations(spec, claim_dir, graph)
    assert errors == []


def test_same_github_user_cannot_fill_both_review_roles(tmp_path: Path) -> None:
    claim_dir, graph, spec = _setup(tmp_path)
    (claim_dir / "reviews/formal.json").write_text(
        json.dumps(_attestation(claim_dir, "same-reviewer", 7, "formal_evidence")),
        encoding="utf-8",
    )
    (claim_dir / "reviews/domain.json").write_text(
        json.dumps(_attestation(claim_dir, "same-reviewer", 7, "domain_semantics")),
        encoding="utf-8",
    )
    errors, _warnings = validate_review_attestations(spec, claim_dir, graph)
    assert any("not independent" in error for error in errors)


def test_author_cannot_be_independent_reviewer(tmp_path: Path) -> None:
    claim_dir, graph, spec = _setup(tmp_path)
    (claim_dir / "reviews/formal.json").write_text(
        json.dumps(_attestation(claim_dir, "author", 1, "formal_evidence")), encoding="utf-8"
    )
    (claim_dir / "reviews/domain.json").write_text(
        json.dumps(_attestation(claim_dir, "domain-reviewer", 2, "domain_semantics")),
        encoding="utf-8",
    )
    errors, _warnings = validate_review_attestations(spec, claim_dir, graph)
    assert any("author/merging maintainer" in error for error in errors)


def test_reviewed_artifact_hash_is_bound(tmp_path: Path) -> None:
    claim_dir, graph, spec = _setup(tmp_path)
    formal = _attestation(claim_dir, "formal-reviewer", 1, "formal_evidence")
    formal["reviewed_artifacts"][0]["sha256"] = "0" * 64
    (claim_dir / "reviews/formal.json").write_text(json.dumps(formal), encoding="utf-8")
    (claim_dir / "reviews/domain.json").write_text(
        json.dumps(_attestation(claim_dir, "domain-reviewer", 2, "domain_semantics")),
        encoding="utf-8",
    )
    errors, _warnings = validate_review_attestations(spec, claim_dir, graph)
    assert any("hash mismatch" in error for error in errors)

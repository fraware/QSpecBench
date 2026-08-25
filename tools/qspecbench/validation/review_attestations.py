"""Validation for authenticated review-attestation v2 sidecars."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

from qspecbench.artifacts import claim_path_escape_error, resolve_claim_path

SCHEMA_FILE = "review_attestation_v2.schema.json"
REQUIRED_PROMOTION_ROLES = {"formal_evidence", "domain_semantics"}


def _repo_root(start: Path) -> Path:
    probe = start.resolve()
    for candidate in (probe, *probe.parents):
        if (candidate / "schema" / SCHEMA_FILE).is_file():
            return candidate
    return probe


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_review_attestations(
    spec: dict[str, Any], claim_dir: Path, graph: dict[str, Any] | None
) -> tuple[list[str], list[str]]:
    """Validate attestation paths declared by an assurance graph.

    Absence remains a migration warning for promoted claims; once paths are declared they
    are fail-closed. This avoids falsely authenticating legacy reviewer aliases while still
    allowing the corpus to migrate incrementally.
    """
    errors: list[str] = []
    warnings: list[str] = []
    maturity = (spec.get("status") or {}).get("maturity")
    promoted = maturity in {"reference_claim", "artifact_bound_reference_claim"}

    if graph is None:
        return errors, warnings

    paths = graph.get("review_attestations") or []
    if not paths:
        if promoted:
            warnings.append(
                "promoted claim has no authenticated review-attestation v2 records; issue #12 blocks governance-grade promotion"
            )
        return errors, warnings

    root = _repo_root(claim_dir)
    try:
        schema = json.loads((root / "schema" / SCHEMA_FILE).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"review attestation schema unavailable: {exc}"], warnings

    proposition_id = ((graph.get("proposition") or {}).get("id") or "").strip()
    authorship = spec.get("authorship") or {}
    prohibited_logins = {
        str(authorship.get("author") or "").strip().lower(),
        str(authorship.get("merging_maintainer") or "").strip().lower(),
    } - {""}

    reviewer_ids: set[int] = set()
    roles: set[str] = set()
    for rel_path in paths:
        escape = claim_path_escape_error(claim_dir, rel_path)
        if escape:
            errors.append(f"review attestation {rel_path}: {escape}")
            continue
        full = resolve_claim_path(claim_dir, rel_path)
        if not full.is_file():
            errors.append(f"missing review attestation: {rel_path}")
            continue
        try:
            payload = json.loads(full.read_text(encoding="utf-8"))
            jsonschema.validate(payload, schema)
        except (OSError, json.JSONDecodeError, jsonschema.ValidationError) as exc:
            errors.append(f"review attestation {rel_path}: {exc}")
            continue

        if payload.get("benchmark_id") != spec.get("id"):
            errors.append(f"review attestation {rel_path}: benchmark_id mismatch")
        if payload.get("proposition_id") != proposition_id:
            errors.append(f"review attestation {rel_path}: proposition_id mismatch")

        reviewer = payload.get("reviewer") or {}
        reviewer_id = reviewer.get("github_user_id")
        login = str(reviewer.get("github_login") or "").strip().lower()
        if reviewer_id in reviewer_ids:
            errors.append(
                f"review attestation {rel_path}: reviewer github_user_id {reviewer_id} is not independent"
            )
        if isinstance(reviewer_id, int):
            reviewer_ids.add(reviewer_id)
        if login in prohibited_logins:
            errors.append(
                f"review attestation {rel_path}: author/merging maintainer cannot satisfy independent review"
            )
        from qspecbench.reviews import FORBIDDEN_REVIEWER_ALIASES, is_unauthenticated_legacy_reviewer

        if login in {alias.lower() for alias in FORBIDDEN_REVIEWER_ALIASES} or is_unauthenticated_legacy_reviewer(
            login
        ):
            errors.append(
                f"review attestation {rel_path}: reviewer {login!r} is an unauthenticated "
                "alias and cannot satisfy independent review"
            )
        roles.add(str(payload.get("role") or ""))

        accepted = set(payload.get("accepted_obligations") or [])
        graph_obligations = {x.get("id") for x in graph.get("obligations", []) if x.get("id")}
        unknown = sorted(accepted - graph_obligations)
        if unknown:
            errors.append(
                f"review attestation {rel_path}: accepts unknown obligations: {unknown}"
            )

        for artifact in payload.get("reviewed_artifacts", []):
            artifact_path = artifact.get("path")
            if not artifact_path:
                continue
            escape = claim_path_escape_error(claim_dir, artifact_path)
            if escape:
                errors.append(f"review attestation {rel_path}: reviewed artifact: {escape}")
                continue
            full_artifact = resolve_claim_path(claim_dir, artifact_path)
            if not full_artifact.is_file():
                errors.append(
                    f"review attestation {rel_path}: missing reviewed artifact {artifact_path}"
                )
                continue
            actual = _sha256(full_artifact)
            if actual != artifact.get("sha256"):
                errors.append(
                    f"review attestation {rel_path}: reviewed artifact hash mismatch for {artifact_path}"
                )

    if promoted:
        missing_roles = sorted(REQUIRED_PROMOTION_ROLES - roles)
        if missing_roles:
            errors.append(
                "authenticated review attestations do not cover required promotion roles: "
                + ", ".join(missing_roles)
            )
    return errors, warnings

"""Schema dialect enforcement keyed on ``qspecbench_version``.

Fail-closed rules:

* ``0.1`` — legacy fields only (no scoped maturity / artifact-bound / 0.3 anchors)
* ``0.2`` — scoped maturity allowed; ``artifact_bound_reference_claim`` and 0.3-only
  bridge/review anchors forbidden
* ``0.3`` — permits artifact-bound maturity, elaborator hash, AST authority, promotion
  review artifact fields (enforced elsewhere when maturity requires them)
"""

from __future__ import annotations

from typing import Any

ARTIFACT_BOUND_LEVEL = "artifact_bound_reference_claim"

# Fields introduced in schema 0.2 (forbidden on 0.1).
V02_ONLY_ROOT_FIELDS: frozenset[str] = frozenset(
    {
        "claim_scope",
        "proved_scope",
        "headline_claim_status",
        "proof_obligations",
        "formal_claims",
        "semantics_base",
        "qasm_extraction",
        "claim_identity",
        "authorship",
    }
)

# Maturity values introduced with scoped reference levels (0.2+).
V02_MATURITY: frozenset[str] = frozenset(
    {
        "reference_scaffold",
        "reference_contract",
        "reference_artifact",
        "reference_claim",
        "artifact_bound_reference_claim",
    }
)

# Bridge / review anchors that require schema 0.3.
V03_BRIDGE_FIELDS: frozenset[str] = frozenset(
    {
        "theorem_elaborator_hash",
        "ast_authority",
        "lean_ast_sha256",
    }
)

V03_REVIEW_FIELDS: frozenset[str] = frozenset(
    {
        "review_artifact_path",
        "review_artifact_sha256",
        "review_commit",
    }
)


def _bridge_dict(spec: dict[str, Any]) -> dict[str, Any] | None:
    bridge = spec.get("semantic_bridge")
    return bridge if isinstance(bridge, dict) else None


def validate_schema_dialect(spec: dict[str, Any]) -> list[str]:
    """Return dialect errors for a loaded spec (empty if compliant)."""
    errors: list[str] = []
    version = str(spec.get("qspecbench_version") or "").strip()
    if version not in {"0.1", "0.2", "0.3"}:
        errors.append(
            f"qspecbench_version must be '0.1', '0.2', or '0.3' (got {version!r})"
        )
        return errors

    maturity = (spec.get("status") or {}).get("maturity")
    bridge = _bridge_dict(spec)
    reviews = (spec.get("status") or {}).get("reviews") or {}

    if version == "0.1":
        for field in V02_ONLY_ROOT_FIELDS:
            if field in spec:
                errors.append(
                    f"schema 0.1 forbids field {field!r}; migrate to 0.2+ "
                    "(see docs/schema_migration_0.2.md)"
                )
        if maturity in V02_MATURITY:
            errors.append(
                f"schema 0.1 forbids maturity {maturity!r}; use seed/usable/deprecated "
                "or migrate to 0.2+"
            )
        if bridge:
            for field in V03_BRIDGE_FIELDS:
                if bridge.get(field):
                    errors.append(
                        f"schema 0.1 forbids semantic_bridge.{field}; migrate to 0.3"
                    )
        for review_key, block in reviews.items():
            if not isinstance(block, dict):
                continue
            for field in V03_REVIEW_FIELDS:
                if block.get(field):
                    errors.append(
                        f"schema 0.1 forbids status.reviews.{review_key}.{field}; "
                        "migrate to 0.3"
                    )

    elif version == "0.2":
        if maturity == ARTIFACT_BOUND_LEVEL:
            errors.append(
                "schema 0.2 forbids maturity artifact_bound_reference_claim; "
                "bump qspecbench_version to '0.3'"
            )
        if bridge:
            for field in V03_BRIDGE_FIELDS:
                if bridge.get(field):
                    errors.append(
                        f"schema 0.2 forbids semantic_bridge.{field}; "
                        "bump qspecbench_version to '0.3'"
                    )
        for review_key, block in reviews.items():
            if not isinstance(block, dict):
                continue
            for field in V03_REVIEW_FIELDS:
                if block.get(field):
                    errors.append(
                        f"schema 0.2 forbids status.reviews.{review_key}.{field}; "
                        "bump qspecbench_version to '0.3'"
                    )
        if spec.get("claim_identity"):
            errors.append(
                "schema 0.2 forbids claim_identity; bump qspecbench_version to '0.3'"
            )

    # version 0.3: artifact-bound / elaborator / review-artifact obligations are
    # enforced by maturity validators once dialect permits the fields.

    return errors

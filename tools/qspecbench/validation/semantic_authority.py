"""Semantic-authority rules across benchmark specs and assurance graphs.

A benchmark may carry transitional semantic metadata while it is experimental, but a
promoted claim must have exactly one authoritative registered profile. Historical
profiles remain readable for reproducibility and are never silently reinterpreted;
profiles whose implementation contract is ambiguous or declarative-only are instead
forbidden for new promotion.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from qspecbench.semantic_profiles import (
    PROMOTION_FORBIDDEN_PROFILE_IDS,
    ProfileError,
    cross_consistency_errors,
    load_registered_profile,
)

PROMOTED_MATURITIES = {"reference_claim", "artifact_bound_reference_claim"}


def _load_graph_profile_id(claim_dir: Path) -> str | None:
    graph_path = claim_dir / "assurance_graph.yaml"
    if not graph_path.is_file():
        return None
    try:
        graph = yaml.safe_load(graph_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        # The assurance-graph validator reports the primary parse/schema failure.
        return None
    if not isinstance(graph, dict):
        return None
    profile = graph.get("semantic_profile") or {}
    profile_id = profile.get("id")
    return str(profile_id) if profile_id else None


def validate_semantic_authority(
    spec: dict[str, Any],
    claim_dir: Path,
) -> tuple[list[str], list[str]]:
    """Check that profile identity and executable semantics are promotion-safe.

    Existing experimental packages are allowed to expose an explicit migration
    warning when ``spec.openqasm_profile`` and the assurance-graph profile differ.
    Promoted packages fail closed on that mismatch and on historical profiles whose
    semantics are not eligible for promotion.
    """
    errors: list[str] = []
    warnings: list[str] = []
    maturity = str((spec.get("status") or {}).get("maturity") or "")
    promoted = maturity in PROMOTED_MATURITIES

    spec_profile = spec.get("openqasm_profile")
    spec_profile_id = str(spec_profile) if spec_profile else None
    graph_profile_id = _load_graph_profile_id(claim_dir)

    if spec_profile_id and graph_profile_id and spec_profile_id != graph_profile_id:
        message = (
            "semantic authority mismatch: spec.openqasm_profile must equal assurance "
            "graph semantic_profile.id "
            f"(spec={spec_profile_id!r}, graph={graph_profile_id!r})"
        )
        if promoted:
            errors.append(message)
        else:
            warnings.append(message + "; transitional experimental package is not promotion-safe")

    effective_profile_ids = {
        profile_id for profile_id in (spec_profile_id, graph_profile_id) if profile_id
    }
    for profile_id in sorted(effective_profile_ids):
        try:
            profile = load_registered_profile(profile_id)
        except ProfileError:
            # Dedicated schema/assurance validation owns the missing-profile error.
            continue
        consistency = cross_consistency_errors(profile)
        errors.extend(f"semantic profile {profile_id}: {error}" for error in consistency)

        if profile_id in PROMOTION_FORBIDDEN_PROFILE_IDS:
            message = (
                f"semantic profile {profile_id!r} is historical/reproducibility-only and "
                "is not eligible for promoted claims"
            )
            if promoted:
                errors.append(message)
            else:
                warnings.append(message)

    return errors, warnings

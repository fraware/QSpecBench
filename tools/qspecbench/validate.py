"""Validation of spec.yaml files and benchmark layout.

Public facade — implementation lives under ``qspecbench.validation``.
CLI and tests should keep importing from ``qspecbench.validate``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import jsonschema
import yaml

from qspecbench.artifact_schemas import validate_claim_artifacts
from qspecbench.artifacts import check_layout, claim_dir_for_spec, find_spec_files
from qspecbench.models import validate_spec_trust_slice
from qspecbench.schema import validate_spec_schema
from qspecbench.trust import validate_trust_rules
from qspecbench.validation.assurance import validate_assurance_graph_rules
from qspecbench.validation.bridges import (  # noqa: F401 — re-export
    validate_semantic_bridge_rules,
)
from qspecbench.validation.claims import validate_claim_rules
from qspecbench.validation.evidence import (
    validate_dynamic_circuit_qubit_limit,
    validate_evidence_rules,
)
from qspecbench.validation.layout import validate_layout_rules
from qspecbench.validation.profile_conformance import validate_assurance_profile_conformance
from qspecbench.validation.provenance import validate_provenance_rules
from qspecbench.validation.qec import (  # noqa: F401 — re-export for tests
    infer_qec_witness_claim_kind,
    validate_qec_witness_file,
)
from qspecbench.validation.result import ValidationResult, load_spec
from qspecbench.validation.reviews import validate_review_rules
from qspecbench.validation.schema import validate_openqasm_profile, validate_schema_rules
from qspecbench.validation.semantic_authority import validate_semantic_authority

# Back-compat aliases used by older tests / scripts.
_infer_qec_witness_claim_kind = infer_qec_witness_claim_kind
_validate_qec_witness_file = validate_qec_witness_file


def validate_spec_dict(
    spec: dict[str, Any], claim_dir: Path, benchmarks_root: Path
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        validate_spec_schema(spec)
    except jsonschema.ValidationError as exc:
        errors.append(f"schema: {exc.message}")
        return errors, warnings

    errors.extend(validate_layout_rules(spec, claim_dir, benchmarks_root))
    errors.extend(validate_schema_rules(spec))
    errors.extend(validate_openqasm_profile(spec, claim_dir))
    errors.extend(validate_spec_trust_slice(spec))
    errors.extend(check_layout(claim_dir))
    errors.extend(validate_trust_rules(spec, claim_dir))
    errors.extend(validate_provenance_rules(spec, claim_dir))
    errors.extend(validate_review_rules(spec, claim_dir))
    errors.extend(validate_claim_rules(spec, claim_dir))
    errors.extend(validate_evidence_rules(spec, claim_dir))
    assurance_errors, assurance_warnings = validate_assurance_graph_rules(spec, claim_dir)
    errors.extend(assurance_errors)
    warnings.extend(assurance_warnings)
    authority_errors, authority_warnings = validate_semantic_authority(spec, claim_dir)
    errors.extend(authority_errors)
    warnings.extend(authority_warnings)
    errors.extend(validate_assurance_profile_conformance(spec, claim_dir))
    warnings.extend(validate_dynamic_circuit_qubit_limit(claim_dir, spec))
    errors.extend(validate_claim_artifacts(spec, claim_dir))
    errors.extend(validate_qec_witness_file(claim_dir, spec))
    bridge_errors, bridge_warnings = validate_semantic_bridge_rules(spec, claim_dir)
    errors.extend(bridge_errors)
    warnings.extend(bridge_warnings)
    return errors, warnings


def validate_path(target: Path) -> list[ValidationResult]:
    original = target.resolve()
    benchmarks_root = original if original.name == "benchmarks" else None
    probe = original
    if benchmarks_root is None:
        while probe.name != "benchmarks" and probe.parent != probe:
            probe = probe.parent
        benchmarks_root = probe if probe.name == "benchmarks" else probe.parent

    results: list[ValidationResult] = []
    for spec_path in find_spec_files(original):
        claim_dir = claim_dir_for_spec(spec_path)
        try:
            spec = load_spec(spec_path)
        except yaml.YAMLError as exc:
            results.append(ValidationResult(spec_path, [f"yaml parse error: {exc}"]))
            continue
        errors, warnings = validate_spec_dict(spec, claim_dir, benchmarks_root)
        results.append(ValidationResult(spec_path, errors, warnings))
    return results


__all__ = [
    "ValidationResult",
    "load_spec",
    "validate_path",
    "validate_spec_dict",
    "validate_semantic_bridge_rules",
    "find_spec_files",
    "_infer_qec_witness_claim_kind",
    "_validate_qec_witness_file",
]

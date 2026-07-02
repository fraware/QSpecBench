"""Validation of spec.yaml files and benchmark layout."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import jsonschema
import yaml

from qspecbench.artifacts import (
    check_layout,
    claim_dir_for_spec,
    claim_path_escape_error,
    find_spec_files,
    resolve_claim_path,
    track_for_claim,
)
from qspecbench.schema import REPO_ROOT, validate_spec_schema
from qspecbench.models import ALL_REFERENCE_LEVELS, REFERENCE_CLAIM_LEVEL, validate_spec_trust_slice
from qspecbench.trust import validate_trust_rules
from qspecbench.artifact_schemas import validate_claim_artifacts
from qspecbench.bridge_manifest import validate_kernel_checked_bridge, validate_manifest_bridge
from qspecbench.bridge_codegen import (
    KERNEL_BRIDGE_IDS,
    KERNEL_CHECKED_LINK,
    LEGACY_KERNEL_CHECKED_LINK,
    AST_AUTHORITY_FIELD,
    AST_AUTHORITY_LEAN_MIRROR,
    is_kernel_checked_link,
    read_theorem_source_hash,
    theorem_source_statement_hash,
    verify_kernel_artifact_semantics_bridge,
    _elaborator_exported_types,
)
from qspecbench.provenance import validate_provenance
from qspecbench.verify_bridge import verify_bridge

# Bridge links that assert a verified equality between the QASM matrix and the
# OpenQASM3 denotation model (Python-level consistency or manifest binding).
VERIFIED_BRIDGE_LINKS = {
    "python_denotation_consistency",
    "manifest_checked_theorem_binding",
    KERNEL_CHECKED_LINK,
    LEGACY_KERNEL_CHECKED_LINK,
    # Deprecated aliases (rejected at validation).
    "python_consistency_checked",
    "kernel_checked",
}

ARTIFACT_BOUND_LEVEL = "artifact_bound_reference_claim"
REQUIRED_ARTIFACT_BOUND_REVIEWS = ("formal_evidence_review", "domain_semantics_review")

SNAKE_CASE = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass
class ValidationResult:
    spec_path: Path
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def load_spec(spec_path: Path) -> dict[str, Any]:
    with spec_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if data is None:
        raise ValueError(f"Empty or invalid YAML in {spec_path}")
    return data


def _load_semantic_bridge(spec: dict[str, Any], claim_dir: Path) -> dict[str, Any] | None:
    inline = spec.get("semantic_bridge")
    if isinstance(inline, dict):
        return inline
    bridge_path = claim_dir / "expected" / "semantic_bridge.json"
    if bridge_path.is_file():
        try:
            return json.loads(bridge_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
    return None


def _has_qasm_objects(spec: dict[str, Any]) -> bool:
    return any(
        obj.get("format") in {"qasm2", "qasm3"} and obj.get("path") for obj in spec.get("objects", [])
    )


def _has_lean_evidence(spec: dict[str, Any]) -> bool:
    return any(e.get("type") == "lean_proof" for e in spec.get("evidence", []))


def _has_passing_bridge_verify(spec: dict[str, Any]) -> bool:
    for ev in spec.get("evidence", []):
        if ev.get("status") != "passing":
            continue
        checker = (ev.get("checker") or "").lower()
        eid = (ev.get("id") or "").lower()
        if "verify-bridge" in checker or "verify_bridge" in checker or eid == "bridge_verify":
            return True
    return False


def _validate_kernel_bridge_authority_warnings(
    spec: dict[str, Any], bridge: dict[str, Any] | None
) -> list[str]:
    """Non-fatal warnings for v0.3 hash/AST authority transition on kernel bridges."""
    warnings: list[str] = []
    if not bridge:
        return warnings
    benchmark_id = spec.get("id", "")
    if benchmark_id not in KERNEL_BRIDGE_IDS:
        return warnings
    if not is_kernel_checked_link(bridge.get("claimed_link")):
        return warnings

    has_elab = benchmark_id in _elaborator_exported_types()
    bridge_source = read_theorem_source_hash(bridge)
    expected_source = theorem_source_statement_hash(benchmark_id)
    if has_elab and expected_source and bridge_source and bridge_source != expected_source:
        warnings.append(
            f"theorem_source_statement_hash differs from syntactic regex extraction for "
            f"{benchmark_id}; theorem_elaborator_hash is primary authority (v0.3)"
        )
    elif has_elab and expected_source and not bridge_source:
        warnings.append(
            f"theorem_source_statement_hash missing for {benchmark_id}; "
            "theorem_elaborator_hash is primary authority (v0.3)"
        )

    authority = bridge.get(AST_AUTHORITY_FIELD)
    if authority and authority != AST_AUTHORITY_LEAN_MIRROR:
        warnings.append(
            f"semantic_bridge.ast_authority={authority!r}; kernel bridges should use "
            f"{AST_AUTHORITY_LEAN_MIRROR!r}"
        )
    lean_ast = bridge.get("lean_ast_sha256")
    py_ast = bridge.get("ast_sha256")
    if lean_ast and py_ast and lean_ast != py_ast:
        warnings.append(
            f"lean_ast_sha256 != ast_sha256 for {benchmark_id}; "
            "Lean-mirror parse is sole AST authority for kernel bridges"
        )
    return warnings


def validate_semantic_bridge_rules(spec: dict[str, Any], claim_dir: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    maturity = spec.get("status", {}).get("maturity")
    bridge = _load_semantic_bridge(spec, claim_dir)
    if (
        maturity in ALL_REFERENCE_LEVELS
        and _has_qasm_objects(spec)
        and _has_lean_evidence(spec)
        and bridge is None
    ):
        errors.append(
            f"{maturity} with QASM artifacts and Lean evidence requires semantic_bridge "
            "(spec root or expected/semantic_bridge.json)"
        )
    claimed_link = bridge.get("claimed_link") if bridge else None
    if claimed_link in {"python_consistency_checked", "kernel_checked"}:
        errors.append(
            f"claimed_link {claimed_link!r} is deprecated; use "
            "python_denotation_consistency or manifest_checked_theorem_binding"
        )
    if claimed_link in {
        "python_denotation_consistency",
        "manifest_checked_theorem_binding",
        KERNEL_CHECKED_LINK,
        LEGACY_KERNEL_CHECKED_LINK,
    }:
        if not _has_passing_bridge_verify(spec):
            errors.append(
                f"claimed_link {claimed_link} requires passing bridge verify evidence "
                "(checker verify-bridge or evidence id bridge_verify)"
            )
        else:
            result = verify_bridge(claim_dir)
            if not result.get("ok"):
                errors.append(
                    f"claimed_link {claimed_link} requires verify-bridge matrix match: "
                    + "; ".join(result.get("errors", []))
                )
        if claimed_link == "manifest_checked_theorem_binding":
            errors.extend(validate_manifest_bridge(claim_dir, bridge, spec))
        if is_kernel_checked_link(claimed_link):
            errors.extend(validate_kernel_checked_bridge(claim_dir, bridge, spec))
            if claimed_link == LEGACY_KERNEL_CHECKED_LINK:
                errors.extend(
                    verify_kernel_artifact_semantics_bridge(bridge, spec.get("id", claim_dir.name))
                )
    errors.extend(_validate_wire_order(spec, bridge))
    errors.extend(_validate_reference_claim_bridge(spec, bridge))
    errors.extend(_validate_artifact_bound_reference_claim(spec, claim_dir, bridge))
    errors.extend(_validate_qec_claim_scope(spec, claim_dir))
    warnings.extend(_validate_kernel_bridge_authority_warnings(spec, bridge))
    return errors, warnings


def _validate_artifact_bound_reference_claim(
    spec: dict[str, Any],
    claim_dir: Path,
    bridge: dict[str, Any] | None,
) -> list[str]:
    """Fail closed on artifact_bound_reference_claim until full promotion obligations are met."""
    errors: list[str] = []
    maturity = spec.get("status", {}).get("maturity")
    if maturity != ARTIFACT_BOUND_LEVEL:
        return errors

    headline = spec.get("headline_claim_status") or {}
    if headline.get("status") != "checked":
        errors.append(
            f"{ARTIFACT_BOUND_LEVEL} requires headline_claim_status.status: checked"
        )

    reviews = (spec.get("status") or {}).get("reviews") or {}
    for review_key in REQUIRED_ARTIFACT_BOUND_REVIEWS:
        block = reviews.get(review_key) or {}
        status = block.get("status")
        reviewer = (block.get("reviewer") or "").strip()
        if status not in {"approved", "required"}:
            errors.append(
                f"{ARTIFACT_BOUND_LEVEL} requires status.reviews.{review_key}.status "
                "approved or required"
            )
        if not reviewer or reviewer == "maintainer-bootstrap":
            errors.append(
                f"{ARTIFACT_BOUND_LEVEL} requires status.reviews.{review_key}.reviewer "
                "with a named non-bootstrap identity"
            )

    if not bridge:
        errors.append(
            f"{ARTIFACT_BOUND_LEVEL} requires semantic_bridge with hash anchors"
        )
        return errors

    if bridge.get("claimed_link") != KERNEL_CHECKED_LINK and bridge.get("claimed_link") != LEGACY_KERNEL_CHECKED_LINK:
        errors.append(
            f"{ARTIFACT_BOUND_LEVEL} requires claimed_link {KERNEL_CHECKED_LINK!r} "
            f"or {LEGACY_KERNEL_CHECKED_LINK!r}"
        )

    for anchor in (
        "artifact_sha256",
        "gate_trace_sha256",
        "ast_sha256",
        "lean_ast_sha256",
        "generated_lean_sha256",
        "theorem_identifier_sha256",
        "theorem_elaborator_hash",
        "theorem_source_statement_hash",
    ):
        if not bridge.get(anchor):
            errors.append(
                f"{ARTIFACT_BOUND_LEVEL} requires semantic_bridge.{anchor} anchor"
            )

    proved = spec.get("proved_scope") or {}
    if proved.get("unproved_obligations"):
        errors.append(
            f"{ARTIFACT_BOUND_LEVEL} requires proved_scope.unproved_obligations to be empty"
        )

    if not _has_passing_bridge_verify(spec):
        errors.append(
            f"{ARTIFACT_BOUND_LEVEL} requires passing bridge verify evidence"
        )

    benchmark_id = spec.get("id", "")
    from qspecbench.bridge_metadata import KERNEL_BRIDGE_METADATA, verify_bridge_metadata_against_manifest

    metadata_def = next(
        (def_name for def_name, mapped_id in KERNEL_BRIDGE_METADATA.items() if mapped_id == benchmark_id),
        None,
    )
    if metadata_def is None:
        errors.append(
            f"{ARTIFACT_BOUND_LEVEL} requires Lean BridgeMetadata pin for {benchmark_id!r}"
        )
    else:
        errors.extend(verify_bridge_metadata_against_manifest(metadata_def))

    return errors


def _validate_ai_formalization_reviewer(spec: dict[str, Any]) -> list[str]:
    """Hard-fail ai_formalization reference_claim without named reviewer identity."""
    errors: list[str] = []
    if spec.get("track") != "ai_formalization":
        return errors
    maturity = spec.get("status", {}).get("maturity")
    if maturity != REFERENCE_CLAIM_LEVEL:
        return errors
    reviews = (spec.get("status") or {}).get("reviews") or {}
    for review_key in REQUIRED_ARTIFACT_BOUND_REVIEWS:
        block = reviews.get(review_key) or {}
        reviewer = (block.get("reviewer") or "").strip()
        if not reviewer:
            errors.append(
                f"ai_formalization {REFERENCE_CLAIM_LEVEL} requires "
                f"status.reviews.{review_key}.reviewer (named identity)"
            )
        elif reviewer == "maintainer-bootstrap":
            errors.append(
                f"ai_formalization {REFERENCE_CLAIM_LEVEL} requires "
                f"status.reviews.{review_key}.reviewer to be non-bootstrap"
            )
    return errors


def _validate_wire_order(spec: dict[str, Any], bridge: dict[str, Any] | None) -> list[str]:
    errors: list[str] = []
    if not bridge:
        return errors
    wire_order = bridge.get("wire_order")
    if not wire_order:
        errors.append("semantic_bridge requires wire_order {model, checked_against}")
        return errors
    model = wire_order.get("model")
    checked = wire_order.get("checked_against")
    if model not in {"legacy_kron_order", "openqasm_little_endian_wire_order"}:
        errors.append(f"wire_order.model invalid: {model!r}")
    if checked not in {"lean", "python_operational", "both"}:
        errors.append(f"wire_order.checked_against invalid: {checked!r}")
    claimed = bridge.get("claimed_link")
    if is_kernel_checked_link(claimed) and checked not in {"lean", "both"}:
        errors.append(
            f"kernel-checked bridge requires wire_order.checked_against in {{lean, both}}, got {checked!r}"
        )
    wire_thm = bridge.get("wire_order_bridge_theorem")
    if wire_thm:
        parser_lean = REPO_ROOT / "lean" / "QSpecBench" / "Quantum" / "OpenQASM3Parser.lean"
        openqasm3 = REPO_ROOT / "lean" / "QSpecBench" / "Quantum" / "OpenQASM3.lean"
        found = False
        for lean_path in (openqasm3, parser_lean):
            if lean_path.is_file():
                text = lean_path.read_text(encoding="utf-8")
                if f"theorem {wire_thm}" in text or f"lemma {wire_thm}" in text:
                    found = True
                    break
        if not found:
            errors.append(
                f"wire_order_bridge_theorem {wire_thm!r} not found in OpenQASM3.lean "
                "or OpenQASM3Parser.lean"
            )
    return errors


def _validate_reference_claim_bridge(spec: dict[str, Any], bridge: dict[str, Any] | None) -> list[str]:
    errors: list[str] = []
    if spec.get("status", {}).get("maturity") != REFERENCE_CLAIM_LEVEL or not bridge:
        return errors
    headline = spec.get("headline_claim_status") or {}
    checked_under = headline.get("checked_under") or []
    not_checked = headline.get("not_checked_under") or []
    if is_kernel_checked_link(bridge.get("claimed_link")):
        if KERNEL_CHECKED_LINK not in checked_under and LEGACY_KERNEL_CHECKED_LINK not in checked_under:
            errors.append(
                f"reference_claim kernel bridge requires headline_claim_status.checked_under "
                f"to include {KERNEL_CHECKED_LINK!r}"
            )
        for required in ("full_openqasm3", "hardware_semantics"):
            if required not in not_checked:
                errors.append(
                    f"reference_claim kernel bridge requires not_checked_under to include {required!r}"
                )
    return errors


def _infer_qec_witness_claim_kind(spec: dict[str, Any]) -> str | None:
    """Map qec_claim_scope fields to witness claim_kind for semantic validation."""
    claim_id = spec.get("id", "")
    obligations = set(spec.get("proved_scope", {}).get("checked_obligations") or [])
    obligations.update(spec.get("claim_scope", {}).get("required_obligations") or [])
    scope = spec.get("qec_claim_scope") or {}

    if "syndrome_extraction" in claim_id or "syndrome_extraction" in obligations:
        return "syndrome_extraction"
    if scope.get("distance", {}).get("status") in {"checked", "complete"}:
        return "minimum_distance"
    if scope.get("syndrome_table") in {"checked", "complete"}:
        return "syndrome_extraction"
    if scope.get("stabilizer_commutation") in {"checked", "complete"}:
        return "stabilizer_commutation"
    if scope.get("correction_table") in {"checked", "complete"}:
        return "decoder_correctness"
    if scope.get("logical_preservation_small_code") in {"checked", "complete", "assumed"}:
        return "logical_preservation"
    return "logical_preservation"


def _validate_qec_witness_file(claim_dir: Path, spec: dict[str, Any] | None = None) -> list[str]:
    witness_path = claim_dir / "expected" / "qec_witness.json"
    if not witness_path.is_file():
        return []
    try:
        witness = json.loads(witness_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"expected/qec_witness.json invalid JSON: {exc}"]
    from qspecbench.qec_witness import validate_qec_witness

    claim_kind: str | None = None
    if spec is not None:
        claim_kind = _infer_qec_witness_claim_kind(spec)
    return validate_qec_witness(witness, claim_dir, claim_kind=claim_kind)


def _validate_qec_claim_scope(spec: dict[str, Any], claim_dir: Path) -> list[str]:
    errors: list[str] = []
    if spec.get("track") != "qec":
        return errors
    scope = spec.get("qec_claim_scope")
    if not scope:
        return errors

    if scope.get("stabilizer_commutation") == "checked":
        has_lean = any(
            e.get("type") == "lean_proof" and e.get("status") == "passing"
            for e in spec.get("evidence", [])
        )
        if not has_lean:
            errors.append(
                "qec_claim_scope.stabilizer_commutation checked requires passing lean_proof evidence"
            )

    distance = scope.get("distance") or {}
    if distance.get("status") == "checked":
        has_distance_evidence = False
        cert_level = scope.get("qec_certificate_level")
        for ev in spec.get("evidence", []):
            if ev.get("status") != "passing":
                continue
            path = claim_dir / ev.get("path", "")
            if not path.is_file():
                continue
            if ev.get("type") == "qec_verifier_result":
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                    if payload.get("distance_result"):
                        has_distance_evidence = True
                except json.JSONDecodeError:
                    pass
        if not has_distance_evidence:
            errors.append(
                "qec_claim_scope.distance.status checked requires distance_result evidence "
                "from QEC adapter bruteforce run"
            )
        if cert_level == "qec_external_certificate_checked":
            has_smt = any(
                e.get("type") == "smt_certificate" and e.get("status") == "passing"
                for e in spec.get("evidence", [])
            )
            if not has_smt:
                errors.append(
                    "qec_certificate_level=qec_external_certificate_checked requires "
                    "passing smt_certificate evidence"
                )
    return errors


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

    claim_id = spec.get("id", "")
    if not SNAKE_CASE.match(claim_id):
        errors.append(f"id must be lowercase snake_case: {claim_id}")
    if claim_dir.name != claim_id:
        errors.append(f"id {claim_id} must match directory name {claim_dir.name}")

    track = track_for_claim(claim_dir, benchmarks_root)
    track_map = {
        "algorithms": "algorithm",
        "equivalence": "equivalence",
        "qec": "qec",
        "hamiltonian": "hamiltonian",
        "ai_formalization": "ai_formalization",
    }
    expected_track = track_map.get(track)
    if expected_track and spec.get("track") != expected_track:
        errors.append(f"track {spec.get('track')} must match parent directory {track}")

    if not (claim_dir / "README.md").is_file():
        errors.append("missing README.md claim card")

    spec_block = spec.get("specification", {})
    pre = spec_block.get("preconditions", [])
    post = spec_block.get("postconditions", [])
    if not pre and not post:
        errors.append("must declare at least one precondition or postcondition")

    mode = spec_block.get("mode")
    approx = spec_block.get("approximation", {})
    if mode == "approximate" and not approx.get("enabled"):
        errors.append("approximate mode requires approximation.enabled true")
    if approx.get("enabled"):
        if not approx.get("metric"):
            errors.append("approximation.enabled requires metric")
        if not approx.get("bound"):
            errors.append("approximation.enabled requires bound")

    resources = spec_block.get("resources", {})
    if resources.get("enabled"):
        keys = ("qubits", "gates", "depth", "t_count", "t_depth", "ancilla", "measurements")
        if not any(resources.get(k) for k in keys) and not resources.get("other"):
            errors.append("resources.enabled requires at least one resource field")

    for obj in spec.get("objects", []):
        path = obj.get("path")
        if not path:
            continue
        escape_err = claim_path_escape_error(claim_dir, path)
        if escape_err:
            errors.append(escape_err)
        elif not resolve_claim_path(claim_dir, path).is_file():
            errors.append(f"missing object file: {path}")

    for ev in spec.get("evidence", []):
        path = ev.get("path")
        if not path:
            continue
        escape_err = claim_path_escape_error(claim_dir, path)
        if escape_err:
            errors.append(escape_err)
        elif not resolve_claim_path(claim_dir, path).is_file():
            errors.append(f"missing evidence file: {path}")

    if spec.get("status", {}).get("maturity") == "deprecated":
        readme = (claim_dir / "README.md").read_text(encoding="utf-8") if (claim_dir / "README.md").is_file() else ""
        if "deprecat" not in readme.lower():
            errors.append("deprecated benchmark README must explain deprecation")

    errors.extend(validate_spec_trust_slice(spec))
    errors.extend(check_layout(claim_dir))
    errors.extend(validate_trust_rules(spec, claim_dir))
    errors.extend(validate_provenance(spec, claim_dir))
    from qspecbench.claim_diff import validate_claim_diff

    errors.extend(validate_claim_diff(claim_dir))
    from qspecbench.dynamic_simulation_evidence import validate_dynamic_simulation_evidence

    errors.extend(validate_dynamic_simulation_evidence(claim_dir, spec))
    warnings.extend(_validate_dynamic_circuit_qubit_limit(claim_dir, spec))
    errors.extend(validate_claim_artifacts(spec, claim_dir))
    errors.extend(_validate_qec_witness_file(claim_dir, spec))
    bridge_errors, bridge_warnings = validate_semantic_bridge_rules(spec, claim_dir)
    errors.extend(bridge_errors)
    warnings.extend(bridge_warnings)
    errors.extend(_validate_qasm_extraction(spec))
    errors.extend(_validate_ai_formalization_reviewer(spec))
    return errors, warnings


def _validate_dynamic_circuit_qubit_limit(claim_dir: Path, spec: dict[str, Any]) -> list[str]:
    """Warn (non-fatal) when dynamic-circuit QASM artifacts exceed operational simulator limit."""
    if spec.get("semantics_base") != "dynamic_circuit":
        return []
    from qspecbench.dynamic_simulator import warn_operational_qubit_limit

    warnings: list[str] = []
    for obj in spec.get("objects", []):
        if obj.get("format") != "qasm3":
            continue
        path = obj.get("path")
        if not path:
            continue
        qasm = claim_dir / path
        warnings.extend(warn_operational_qubit_limit(qasm))
    return warnings


def _validate_qasm_extraction(spec: dict[str, Any]) -> list[str]:
    """Fail closed on unimplemented extraction modes.

    ``full_dynamic_semantics`` is accepted only as a legacy alias for
    ``dynamic_fragment_recording`` when ``semantics_base=dynamic_circuit``.
    """
    extraction = spec.get("qasm_extraction")
    if not extraction:
        return []
    mode = extraction.get("mode")
    effective_mode = "dynamic_fragment_recording" if mode == "full_dynamic_semantics" else mode
    if effective_mode == "dynamic_fragment_recording":
        semantics_base = spec.get("semantics_base")
        if semantics_base != "dynamic_circuit":
            return [
                "qasm_extraction.mode=dynamic_fragment_recording requires "
                "semantics_base=dynamic_circuit (projective measurement stub + "
                "declared non-unitary skips)"
            ]
        allowed = set(extraction.get("allowed_to_skip") or [])
        if "measurement" not in allowed:
            return [
                "dynamic_fragment_recording requires allowed_to_skip to include "
                "'measurement' (projective POVM stub; unitary fragment insufficient)"
            ]
    return []


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

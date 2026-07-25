"""Semantic bridge and artifact-bound claim validation."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from qspecbench.bridge_codegen import (
    KERNEL_BRIDGE_IDS,
    KERNEL_CHECKED_LINK,
    LEGACY_KERNEL_CHECKED_LINK,
    DYNAMIC_CHECKED_LINK,
    DYNAMIC_CHECKED_LINKS,
    DYNAMIC_DENOTATION_LINK,
    AST_AUTHORITY_FIELD,
    AST_AUTHORITY_LEAN_MIRROR,
    is_kernel_checked_link,
    is_dynamic_ast_checked_link,
    is_dynamic_denotation_link,
    read_theorem_source_hash,
    theorem_source_statement_hash,
    verify_kernel_artifact_semantics_bridge,
    _elaborator_exported_types,
)
from qspecbench.bridge_manifest import validate_kernel_checked_bridge, validate_manifest_bridge
from qspecbench.models import ALL_REFERENCE_LEVELS, REFERENCE_CLAIM_LEVEL
from qspecbench.schema import REPO_ROOT
from qspecbench.verify_bridge import verify_bridge
from qspecbench.verify_dynamic_ast_bridge import (
    verify_dynamic_ast_bridge,
    verify_dynamic_denotation_bridge,
)
from qspecbench.validation.qec import validate_qec_claim_scope

ARTIFACT_BOUND_LEVEL = "artifact_bound_reference_claim"


def _recompute_bridge_verify() -> bool:
    """Default recompute; set QSPECBENCH_RECOMPUTE_BRIDGE=0 when a bridge job owns it."""
    raw = os.environ.get("QSPECBENCH_RECOMPUTE_BRIDGE", "1").strip().lower()
    return raw not in {"0", "false", "no"}


def _load_committed_bridge_verify(claim_dir: Path) -> dict[str, Any] | None:
    for rel in (
        "evidence/bridge_verify.result.json",
        "evidence/bridge_verify.json",
    ):
        path = claim_dir / rel
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
        if isinstance(payload, dict):
            return payload
    return None

def _load_semantic_bridge(spec: dict[str, Any], claim_dir: Path) -> dict[str, Any] | None:
    inline = spec.get("semantic_bridge")
    if isinstance(inline, dict):
        return inline
    bridge_path = claim_dir / "expected" / "semantic_bridge.json"
    if bridge_path.is_file():
        try:
            return json.loads(bridge_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return {"__parse_error__": f"invalid JSON in expected/semantic_bridge.json: {exc}"}
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


def _has_passing_dynamic_ast_verify(spec: dict[str, Any]) -> bool:
    for ev in spec.get("evidence", []):
        if ev.get("status") != "passing":
            continue
        checker = (ev.get("checker") or "").lower()
        eid = (ev.get("id") or "").lower()
        if (
            "verify-dynamic-ast" in checker
            or "verify_dynamic_ast" in checker
            or eid in {"dynamic_ast_bridge_verify", "bridge_verify_dynamic"}
        ):
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
    if isinstance(bridge, dict) and "__parse_error__" in bridge:
        errors.append(bridge["__parse_error__"])
        return errors, warnings
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
    if is_dynamic_ast_checked_link(claimed_link):
        if not _has_passing_dynamic_ast_verify(spec):
            errors.append(
                f"claimed_link {claimed_link} requires passing dynamic AST verify evidence "
                "(checker verify-dynamic-ast-bridge or evidence id dynamic_ast_bridge_verify)"
            )
        else:
            # kernel_checked_dynamic_denotation is strictly stronger than the plain AST-only
            # link: it must additionally bind to Measurement/ClassicalReg denotation via its
            # own DynamicDenotationBridgeMetadata pin, never a bare AST hash pin.
            if is_dynamic_denotation_link(claimed_link):
                result = verify_dynamic_denotation_bridge(claim_dir)
                if not result.get("ok") or not result.get("denotation_match"):
                    errors.append(
                        f"claimed_link {claimed_link} requires denotation_match: "
                        + "; ".join(result.get("errors", []) or ["denotation_match false"])
                    )
            else:
                result = verify_dynamic_ast_bridge(claim_dir)
                if not result.get("ok") or not result.get("dynamic_ast_match"):
                    errors.append(
                        f"claimed_link {claimed_link} requires dynamic_ast_match: "
                        + "; ".join(result.get("errors", []) or ["dynamic_ast_match false"])
                    )
            if result.get("matrix_match") is True:
                errors.append(
                    f"claimed_link {claimed_link} must not claim matrix_match "
                    "(measure+if is outside matrix KERNEL_BRIDGE)"
                )
    elif claimed_link in {
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
            if _recompute_bridge_verify():
                result = verify_bridge(claim_dir)
            else:
                committed = _load_committed_bridge_verify(claim_dir)
                if committed is not None and committed.get("ok"):
                    result = committed
                else:
                    # Fail closed: skipped recompute still needs an ok result on disk.
                    result = verify_bridge(claim_dir)
            if not result.get("ok"):
                errors.append(
                    f"claimed_link {claimed_link} requires verify-bridge matrix match: "
                    + "; ".join(result.get("errors", []))
                )
        if claimed_link == "manifest_checked_theorem_binding":
            if bridge is None:
                errors.append(
                    f"claimed_link {claimed_link} requires semantic_bridge metadata"
                )
            else:
                errors.extend(validate_manifest_bridge(claim_dir, bridge, spec))
        if is_kernel_checked_link(claimed_link):
            if bridge is None:
                errors.append(
                    f"claimed_link {claimed_link} requires semantic_bridge metadata"
                )
            else:
                errors.extend(validate_kernel_checked_bridge(claim_dir, bridge, spec))
                if claimed_link == LEGACY_KERNEL_CHECKED_LINK:
                    errors.extend(
                        verify_kernel_artifact_semantics_bridge(
                            bridge, spec.get("id", claim_dir.name)
                        )
                    )
    errors.extend(_validate_wire_order(spec, bridge))
    errors.extend(_validate_reference_claim_bridge(spec, bridge))
    errors.extend(_validate_artifact_bound_reference_claim(spec, claim_dir, bridge))
    errors.extend(validate_qec_claim_scope(spec, claim_dir))
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

    # Dual independent review provenance (including artifact hash binding) is
    # enforced by validate_promotion_reviews for checked headlines.

    if not bridge:
        errors.append(
            f"{ARTIFACT_BOUND_LEVEL} requires semantic_bridge with hash anchors"
        )
        return errors

    claimed = bridge.get("claimed_link")
    if is_dynamic_ast_checked_link(claimed):
        return errors + _validate_dynamic_abrc(spec, claim_dir, bridge)

    if claimed != KERNEL_CHECKED_LINK and claimed != LEGACY_KERNEL_CHECKED_LINK:
        errors.append(
            f"{ARTIFACT_BOUND_LEVEL} requires claimed_link {KERNEL_CHECKED_LINK!r}, "
            f"{LEGACY_KERNEL_CHECKED_LINK!r}, or a dynamic measure+if link"
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
    from qspecbench.bridge_codegen import (
        ELABORATOR_MISSING_MSG,
        elaborator_export_available,
        theorem_elaborator_hash,
        THEOREM_ELABORATOR_HASH_FIELD,
    )

    if not elaborator_export_available(benchmark_id):
        errors.append(ELABORATOR_MISSING_MSG)
    else:
        expected_elab = theorem_elaborator_hash(benchmark_id)
        stored_elab = (bridge or {}).get(THEOREM_ELABORATOR_HASH_FIELD)
        if expected_elab and stored_elab and expected_elab != stored_elab:
            errors.append(
                f"{ARTIFACT_BOUND_LEVEL} {THEOREM_ELABORATOR_HASH_FIELD} drift for {benchmark_id}"
            )

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


def _validate_dynamic_abrc(
    spec: dict[str, Any],
    claim_dir: Path,
    bridge: dict[str, Any],
) -> list[str]:
    """ABRC fork for kernel_checked_dynamic_ast_semantics (no matrix / elaborator codegen)."""
    errors: list[str] = []
    for anchor in (
        "dynamic_artifact_sha256",
        "dynamic_ast_sha256",
        "lean_theorem",
        "proposition_id",
        "qasm_artifact",
    ):
        if not bridge.get(anchor):
            errors.append(
                f"{ARTIFACT_BOUND_LEVEL} dynamic ABRC requires semantic_bridge.{anchor}"
            )
    if bridge.get("artifact_bound_category") not in {
        None,
        DYNAMIC_CHECKED_LINK,
        "kernel_checked_dynamic_ast_semantics",
        "kernel_checked_dynamic_denotation",
    }:
        errors.append(
            f"{ARTIFACT_BOUND_LEVEL} dynamic ABRC artifact_bound_category must be "
            f"a dynamic measure+if link when set"
        )
    # Explicit honesty: never require / accept matrix codegen anchors as substitutes.
    if bridge.get("generated_lean_sha256") and not bridge.get("dynamic_ast_sha256"):
        errors.append(
            f"{ARTIFACT_BOUND_LEVEL} dynamic ABRC must not use generated_lean without "
            "dynamic_ast_sha256 (matrix codegen drops measure+if)"
        )

    proved = spec.get("proved_scope") or {}
    if proved.get("unproved_obligations"):
        errors.append(
            f"{ARTIFACT_BOUND_LEVEL} requires proved_scope.unproved_obligations to be empty"
        )

    claimed_link = bridge.get("claimed_link")
    is_denotation = is_dynamic_denotation_link(claimed_link)

    if not _has_passing_dynamic_ast_verify(spec):
        errors.append(
            f"{ARTIFACT_BOUND_LEVEL} dynamic ABRC requires passing dynamic AST verify evidence"
        )
    elif is_denotation:
        result = verify_dynamic_denotation_bridge(claim_dir)
        if not result.get("ok") or not result.get("denotation_match"):
            errors.append(
                f"{ARTIFACT_BOUND_LEVEL} dynamic ABRC verify failed: "
                + "; ".join(result.get("errors", []) or ["denotation_match false"])
            )
    else:
        result = verify_dynamic_ast_bridge(claim_dir)
        if not result.get("ok") or not result.get("dynamic_ast_match"):
            errors.append(
                f"{ARTIFACT_BOUND_LEVEL} dynamic ABRC verify failed: "
                + "; ".join(result.get("errors", []) or ["dynamic_ast_match false"])
            )

    benchmark_id = spec.get("id", "")
    if is_denotation:
        from qspecbench.bridge_metadata import (
            DYNAMIC_DENOTATION_BRIDGE_METADATA,
            verify_dynamic_denotation_bridge_metadata,
        )

        metadata_def = next(
            (
                def_name
                for def_name, mapped_id in DYNAMIC_DENOTATION_BRIDGE_METADATA.items()
                if mapped_id == benchmark_id
            ),
            None,
        )
        if metadata_def is None:
            errors.append(
                f"{ARTIFACT_BOUND_LEVEL} dynamic ABRC requires Lean "
                f"DynamicDenotationBridgeMetadata pin for {benchmark_id!r}"
            )
        else:
            errors.extend(verify_dynamic_denotation_bridge_metadata(metadata_def))
    else:
        from qspecbench.bridge_metadata import (
            DYNAMIC_AST_BRIDGE_METADATA,
            verify_dynamic_ast_bridge_metadata,
        )

        metadata_def = next(
            (
                def_name
                for def_name, mapped_id in DYNAMIC_AST_BRIDGE_METADATA.items()
                if mapped_id == benchmark_id
            ),
            None,
        )
        if metadata_def is None:
            errors.append(
                f"{ARTIFACT_BOUND_LEVEL} dynamic ABRC requires Lean DynamicAstBridgeMetadata "
                f"pin for {benchmark_id!r}"
            )
        else:
            errors.extend(verify_dynamic_ast_bridge_metadata(metadata_def))

    checked = (spec.get("headline_claim_status") or {}).get("checked_under") or []
    if not any(link in checked for link in DYNAMIC_CHECKED_LINKS):
        errors.append(
            f"{ARTIFACT_BOUND_LEVEL} dynamic ABRC requires headline checked_under "
            f"to include a dynamic measure+if claimed_link"
        )
    not_checked = (spec.get("headline_claim_status") or {}).get("not_checked_under") or []
    for required in (
        "full_openqasm3_dynamic_circuit",
        "hardware_semantics",
        "matrix_kernel_bridge_dynamic_abrc",
    ):
        if required not in not_checked:
            errors.append(
                f"{ARTIFACT_BOUND_LEVEL} dynamic ABRC requires not_checked_under "
                f"to include {required!r}"
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
    if (
        is_kernel_checked_link(claimed) or is_dynamic_ast_checked_link(claimed)
    ) and checked not in {"lean", "both"}:
        errors.append(
            f"kernel/dynamic-checked bridge requires wire_order.checked_against in "
            f"{{lean, both}}, got {checked!r}"
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
    if is_dynamic_ast_checked_link(bridge.get("claimed_link")):
        if not any(link in checked_under for link in DYNAMIC_CHECKED_LINKS):
            errors.append(
                f"reference_claim dynamic AST bridge requires headline_claim_status.checked_under "
                f"to include a dynamic measure+if claimed_link"
            )
        for required in (
            "full_openqasm3_dynamic_circuit",
            "hardware_semantics",
            "matrix_kernel_bridge_dynamic_abrc",
        ):
            if required not in not_checked:
                errors.append(
                    f"reference_claim dynamic AST bridge requires not_checked_under "
                    f"to include {required!r}"
                )
    return errors

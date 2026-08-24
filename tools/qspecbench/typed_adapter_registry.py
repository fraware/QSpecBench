"""Stable adapter identities for the v1 typed adapter protocol.

Legacy schema-0.3 evidence still uses directory names/checker strings. New protocol users
must use these stable IDs so execution identity is not encoded in prose metadata.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TypedAdapterSpec:
    adapter_id: str
    adapter_version: str
    implementation: str
    trust_ceiling: str
    supported_evidence_types: tuple[str, ...]


_TYPED: tuple[TypedAdapterSpec, ...] = (
    TypedAdapterSpec(
        "qspecbench.lean.kernel.v1",
        "1.0.0",
        "lean/parse_result.py",
        "kernel_checked",
        ("lean_proof", "proof_assistant_proof"),
    ),
    TypedAdapterSpec(
        "qspecbench.mqt.qcec.v1",
        "1.0.0",
        "qcec/parse_result.py",
        "externally_trusted",
        ("qcec_result",),
    ),
    TypedAdapterSpec(
        "qspecbench.bridge.verify.v1",
        "1.0.0",
        "bridge/parse_result.py",
        "heuristic",
        ("bridge_verify", "python_denotation_consistency_check", "internal_denotation_consistency"),
    ),
    TypedAdapterSpec(
        "qspecbench.bridge.dynamic_ast.v1",
        "1.0.0",
        "bridge/dynamic_ast_check.py",
        "kernel_checked",
        ("internal_denotation_consistency",),
    ),
    TypedAdapterSpec(
        "qspecbench.bridge.dynamic_denotation.v1",
        "1.0.0",
        "bridge/dynamic_denotation_check.py",
        "kernel_checked",
        ("internal_denotation_consistency",),
    ),
    TypedAdapterSpec(
        "qspecbench.bridge.hardware_isa.v1",
        "1.0.0",
        "bridge/hardware_isa_check.py",
        "externally_trusted",
        ("internal_denotation_consistency",),
    ),
    TypedAdapterSpec(
        "qspecbench.qec.generic.v1",
        "1.0.0",
        "qec/parse_result.py",
        "externally_trusted",
        ("qec_verifier_result",),
    ),
    TypedAdapterSpec(
        "qspecbench.qec.stim_matching.v1",
        "1.0.0",
        "qec/stim_matching_check.py",
        "simulation",
        ("qec_verifier_result",),
    ),
    TypedAdapterSpec(
        "qspecbench.matrix_certificate.v1",
        "1.0.0",
        "matrix_certificate/parse_result.py",
        "independently_checkable",
        ("matrix_certificate",),
    ),
    TypedAdapterSpec(
        "qspecbench.zx.certificate.v1",
        "1.0.0",
        "zx/parse_result.py",
        "independently_checkable",
        ("zx_certificate",),
    ),
)

TYPED_ADAPTERS: dict[str, TypedAdapterSpec] = {item.adapter_id: item for item in _TYPED}


def get_typed_adapter(adapter_id: str) -> TypedAdapterSpec | None:
    return TYPED_ADAPTERS.get(adapter_id)


def validate_typed_adapter_identity(
    adapter_id: str, adapter_version: str, evidence_type: str | None = None
) -> list[str]:
    spec = get_typed_adapter(adapter_id)
    if spec is None:
        return [f"unknown typed adapter id {adapter_id!r}"]
    errors: list[str] = []
    if adapter_version != spec.adapter_version:
        errors.append(
            f"adapter version mismatch for {adapter_id}: request={adapter_version!r}, "
            f"registry={spec.adapter_version!r}"
        )
    if evidence_type is not None and evidence_type not in spec.supported_evidence_types:
        errors.append(
            f"typed adapter {adapter_id} does not support evidence type {evidence_type!r}"
        )
    return errors

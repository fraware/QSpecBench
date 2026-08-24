"""Stable adapter identities for the v1 typed adapter protocol.

Execution identity is represented by a versioned adapter id, never by the human-readable
``checker`` field. Legacy schema-0.3 entries may omit ``adapter`` when their evidence type has
one unambiguous default below. Evidence classes with multiple semantic implementations must
select a typed adapter explicitly.
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
    TypedAdapterSpec("qspecbench.lean.kernel.v1", "1.0.0", "lean/parse_result.py", "kernel_checked", ("lean_proof", "proof_assistant_proof")),
    TypedAdapterSpec("qspecbench.lean_qec.distance.v1", "1.0.0", "lean_qec/parse_result.py", "kernel_checked", ("qec_verifier_result",)),
    TypedAdapterSpec("qspecbench.coq.kernel.v1", "1.0.0", "coq/parse_result.py", "kernel_checked", ("coq_proof",)),
    TypedAdapterSpec("qspecbench.rocq.kernel.v1", "1.0.0", "rocq/parse_result.py", "kernel_checked", ("rocq_proof",)),
    TypedAdapterSpec("qspecbench.isabelle.kernel.v1", "1.0.0", "isabelle/parse_result.py", "kernel_checked", ("isabelle_proof",)),
    TypedAdapterSpec("qspecbench.openqasm.parse.v1", "1.0.0", "qasm/parse_result.py", "externally_trusted", ("qasm_parse",)),
    TypedAdapterSpec("qspecbench.python.simulation.v1", "1.0.0", "python/parse_result.py", "heuristic", ("simulation",)),
    TypedAdapterSpec("qspecbench.dynamic_simulation.v1", "1.0.0", "dynamic_simulation/parse_result.py", "simulation", ("simulation",)),
    TypedAdapterSpec("qspecbench.ai.draft.v1", "1.0.0", "ai_formalization/parse_result.py", "untrusted", ("ai_draft",)),
    TypedAdapterSpec("qspecbench.human_review.v1", "1.0.0", "human_review/parse_result.py", "externally_trusted", ("human_review",)),
    TypedAdapterSpec("qspecbench.sat.certificate.v1", "1.0.0", "sat_certificate/parse_result.py", "independently_checkable", ("sat_certificate",)),
    TypedAdapterSpec("qspecbench.smt.certificate.v1", "1.0.0", "smt/parse_result.py", "independently_checkable", ("smt_certificate",)),
    TypedAdapterSpec("qspecbench.mqt.qcec.v1", "1.0.0", "qcec/parse_result.py", "externally_trusted", ("qcec_result",)),
    TypedAdapterSpec("qspecbench.compiler.peephole.v1", "1.0.0", "compiler_peephole/parse_result.py", "independently_checkable", ("internal_denotation_consistency",)),
    TypedAdapterSpec("qspecbench.bridge.verify.v1", "1.0.0", "bridge/parse_result.py", "heuristic", ("bridge_verify", "python_denotation_consistency_check", "internal_denotation_consistency")),
    TypedAdapterSpec("qspecbench.bridge.dynamic_ast.v1", "1.0.0", "bridge/dynamic_ast_check.py", "kernel_checked", ("internal_denotation_consistency",)),
    TypedAdapterSpec("qspecbench.bridge.dynamic_denotation.v1", "1.0.0", "bridge/dynamic_denotation_check.py", "kernel_checked", ("internal_denotation_consistency",)),
    TypedAdapterSpec("qspecbench.bridge.hardware_isa.v1", "1.0.0", "bridge/hardware_isa_check.py", "externally_trusted", ("internal_denotation_consistency",)),
    TypedAdapterSpec("qspecbench.qec.generic.v1", "1.0.0", "qec/parse_result.py", "externally_trusted", ("qec_verifier_result",)),
    TypedAdapterSpec("qspecbench.qec.stim_matching.v1", "1.0.0", "qec/stim_matching_check.py", "simulation", ("qec_verifier_result",)),
    TypedAdapterSpec("qspecbench.matrix_certificate.v1", "1.0.0", "matrix_certificate/parse_result.py", "independently_checkable", ("matrix_certificate",)),
    TypedAdapterSpec("qspecbench.qbricks.external.v1", "1.0.0", "qbricks/parse_result.py", "externally_trusted", ("qbricks_result",)),
    TypedAdapterSpec("qspecbench.zx.certificate.v1", "1.0.0", "zx/parse_result.py", "independently_checkable", ("zx_certificate",)),
)

TYPED_ADAPTERS: dict[str, TypedAdapterSpec] = {item.adapter_id: item for item in _TYPED}

# Defaults exist only for the repository-wide ordinary interpretation of an evidence type.
# Dynamic bridge, compiler provenance, Stim/PyMatching, and external Lean-QEC distance cases
# override these defaults with an explicit typed id.
DEFAULT_TYPED_ADAPTER_BY_EVIDENCE_TYPE: dict[str, str] = {
    "lean_proof": "qspecbench.lean.kernel.v1",
    "proof_assistant_proof": "qspecbench.lean.kernel.v1",
    "coq_proof": "qspecbench.coq.kernel.v1",
    "rocq_proof": "qspecbench.rocq.kernel.v1",
    "isabelle_proof": "qspecbench.isabelle.kernel.v1",
    "qasm_parse": "qspecbench.openqasm.parse.v1",
    "simulation": "qspecbench.python.simulation.v1",
    "ai_draft": "qspecbench.ai.draft.v1",
    "human_review": "qspecbench.human_review.v1",
    "sat_certificate": "qspecbench.sat.certificate.v1",
    "smt_certificate": "qspecbench.smt.certificate.v1",
    "qcec_result": "qspecbench.mqt.qcec.v1",
    "bridge_verify": "qspecbench.bridge.verify.v1",
    "python_denotation_consistency_check": "qspecbench.bridge.verify.v1",
    "internal_denotation_consistency": "qspecbench.bridge.verify.v1",
    "qec_verifier_result": "qspecbench.qec.generic.v1",
    "matrix_certificate": "qspecbench.matrix_certificate.v1",
    "qbricks_result": "qspecbench.qbricks.external.v1",
    "zx_certificate": "qspecbench.zx.certificate.v1",
}


def get_typed_adapter(adapter_id: str) -> TypedAdapterSpec | None:
    return TYPED_ADAPTERS.get(adapter_id)


def default_typed_adapter(evidence_type: str) -> TypedAdapterSpec | None:
    adapter_id = DEFAULT_TYPED_ADAPTER_BY_EVIDENCE_TYPE.get(evidence_type)
    return get_typed_adapter(adapter_id) if adapter_id else None


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

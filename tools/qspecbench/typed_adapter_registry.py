"""Stable adapter identities for the v1 typed adapter protocol.

Execution identity is represented by a versioned adapter id, never by the human-readable
``checker`` field or an adapter directory name. Legacy schema-0.3 entries may omit ``adapter``
when their evidence type has one unambiguous default. Historical adapter-directory aliases are
accepted only at the spec input boundary and must canonicalize to an exact typed identity before
execution.
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
        "qspecbench.lean_qec.distance.v1",
        "2.0.0",
        "lean_qec/parse_result.py",
        "kernel_checked",
        ("qec_verifier_result",),
    ),
    TypedAdapterSpec(
        "qspecbench.coq.kernel.v1",
        "1.0.0",
        "coq/parse_result.py",
        "kernel_checked",
        ("coq_proof",),
    ),
    TypedAdapterSpec(
        "qspecbench.rocq.kernel.v1",
        "1.0.0",
        "rocq/parse_result.py",
        "kernel_checked",
        ("rocq_proof",),
    ),
    TypedAdapterSpec(
        "qspecbench.isabelle.kernel.v1",
        "1.0.0",
        "isabelle/parse_result.py",
        "kernel_checked",
        ("isabelle_proof",),
    ),
    TypedAdapterSpec(
        "qspecbench.openqasm.parse.v1",
        "1.0.0",
        "qasm/parse_result.py",
        "externally_trusted",
        ("qasm_parse",),
    ),
    TypedAdapterSpec(
        "qspecbench.python.simulation.v1",
        "1.0.0",
        "python/parse_result.py",
        "heuristic",
        ("simulation",),
    ),
    TypedAdapterSpec(
        "qspecbench.dynamic_simulation.v1",
        "1.0.0",
        "dynamic_simulation/parse_result.py",
        "simulation",
        ("simulation",),
    ),
    TypedAdapterSpec(
        "qspecbench.ai.draft.v1",
        "1.0.0",
        "ai_formalization/parse_result.py",
        "untrusted",
        ("ai_draft",),
    ),
    TypedAdapterSpec(
        "qspecbench.human_review.v1",
        "1.0.0",
        "human_review/parse_result.py",
        "externally_trusted",
        ("human_review",),
    ),
    TypedAdapterSpec(
        "qspecbench.sat.certificate.v1",
        "1.0.0",
        "sat_certificate/parse_result.py",
        "independently_checkable",
        ("sat_certificate",),
    ),
    TypedAdapterSpec(
        "qspecbench.smt.certificate.v1",
        "1.0.0",
        "smt/parse_result.py",
        "independently_checkable",
        ("smt_certificate",),
    ),
    TypedAdapterSpec(
        "qspecbench.mqt.qcec.v1",
        "1.0.0",
        "qcec/parse_result.py",
        "externally_trusted",
        ("qcec_result",),
    ),
    TypedAdapterSpec(
        "qspecbench.compiler.peephole.v1",
        "1.0.0",
        "compiler_peephole/parse_result.py",
        "independently_checkable",
        ("internal_denotation_consistency",),
    ),
    TypedAdapterSpec(
        "qspecbench.qiskit.optimize_1q_gates.v1",
        "1.0.0",
        "qiskit_compiler/parse_result.py",
        "independently_checkable",
        ("internal_denotation_consistency",),
    ),
    TypedAdapterSpec(
        "qspecbench.bridge.verify.v1",
        "1.0.0",
        "bridge/parse_result.py",
        "heuristic",
        (
            "bridge_verify",
            "python_denotation_consistency_check",
            "internal_denotation_consistency",
        ),
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
        "qspecbench.qbricks.external.v1",
        "1.0.0",
        "qbricks/parse_result.py",
        "externally_trusted",
        ("qbricks_result",),
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

# Historical schema-0.3 adapter directory names. These aliases are accepted only while loading
# legacy spec entries. They are never assurance-graph identities and never directly select a
# filesystem path. Every alias must resolve to one registered, versioned typed adapter.
LEGACY_TYPED_ADAPTER_ALIASES: dict[str, str] = {
    "qasm": "qspecbench.openqasm.parse.v1",
    "qec": "qspecbench.qec.generic.v1",
    "python": "qspecbench.python.simulation.v1",
    "ai_formalization": "qspecbench.ai.draft.v1",
    "lean": "qspecbench.lean.kernel.v1",
    "lean_qec": "qspecbench.lean_qec.distance.v1",
    "coq": "qspecbench.coq.kernel.v1",
    "rocq": "qspecbench.rocq.kernel.v1",
    "isabelle": "qspecbench.isabelle.kernel.v1",
    "sat_certificate": "qspecbench.sat.certificate.v1",
    "smt": "qspecbench.smt.certificate.v1",
    "qcec": "qspecbench.mqt.qcec.v1",
    "human_review": "qspecbench.human_review.v1",
    "bridge": "qspecbench.bridge.verify.v1",
    "compiler_peephole": "qspecbench.compiler.peephole.v1",
    "qiskit_compiler": "qspecbench.qiskit.optimize_1q_gates.v1",
    "dynamic_simulation": "qspecbench.dynamic_simulation.v1",
    "matrix_certificate": "qspecbench.matrix_certificate.v1",
    "qbricks": "qspecbench.qbricks.external.v1",
    "zx": "qspecbench.zx.certificate.v1",
}

# Trust-class lattice used for overclaim detection. Higher is stronger.
# ``proof_assistant_native_checked`` is a subtype of ``kernel_checked`` (same rank):
# it is the Lean-QEC acceptance class and does not outrank ordinary kernel checking.
TRUST_CLASS_RANK: dict[str, int] = {
    "untrusted": 0,
    "heuristic": 1,
    "simulation": 2,
    "human_review": 3,
    "externally_trusted": 4,
    "independently_checkable": 5,
    "kernel_checked": 6,
    "proof_assistant_native_checked": 6,
}

PROOF_ASSISTANT_NATIVE_CHECKED = "proof_assistant_native_checked"
KERNEL_CHECKED = "kernel_checked"


def proof_assistant_native_checked_is_kernel_subtype(claimed: str, ceiling: str) -> bool:
    """Document native-checked as a subtype of kernel_checked, not an alias."""
    return claimed == PROOF_ASSISTANT_NATIVE_CHECKED and ceiling == KERNEL_CHECKED


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
    """Resolve an exact typed adapter id; legacy aliases are intentionally not accepted."""
    return TYPED_ADAPTERS.get(adapter_id)


def resolve_typed_adapter_identity(
    adapter_identity: str,
    evidence_type: str | None = None,
) -> TypedAdapterSpec | None:
    """Resolve an exact typed id or a historical spec alias to one typed identity.

    This function is the only compatibility boundary for legacy directory aliases. Assurance
    graphs and sidecars continue to require exact typed ids through :func:`get_typed_adapter`.
    """
    typed = get_typed_adapter(adapter_identity)
    if typed is None:
        canonical = LEGACY_TYPED_ADAPTER_ALIASES.get(adapter_identity)
        typed = get_typed_adapter(canonical) if canonical else None
    if typed is None:
        return None
    if evidence_type is not None and evidence_type not in typed.supported_evidence_types:
        return None
    return typed


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

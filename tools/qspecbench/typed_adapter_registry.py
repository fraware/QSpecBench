"""Stable adapter identities for the v1 typed adapter protocol.

Execution identity is represented by a versioned adapter id, never by the human-readable
``checker`` field or an adapter directory name. Built-in adapters use repository-owned Python
implementations. Third-party adapters may register a Python module through the
``qspecbench.adapters`` package entry-point group, but external discovery is disabled unless the
operator explicitly sets ``QSPECBENCH_ENABLE_ADAPTER_PLUGINS=1``. Benchmark data never supplies
an executable filesystem path.
"""

from __future__ import annotations

import importlib.metadata as importlib_metadata
import os
import re
from dataclasses import dataclass
from functools import lru_cache

ENTRY_POINT_GROUP = "qspecbench.adapters"
PLUGIN_ENABLE_ENV = "QSPECBENCH_ENABLE_ADAPTER_PLUGINS"
MAX_EXTERNAL_PLUGIN_TRUST = "externally_trusted"

_ADAPTER_ID_RE = re.compile(r"^[a-z0-9_.-]+$")
_PYTHON_MODULE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$")
_SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:[-+][0-9A-Za-z.-]+)?$"
)


class AdapterRegistryError(ValueError):
    """Raised when typed-adapter registration is ambiguous or malformed."""


@dataclass(frozen=True)
class TypedAdapterSpec:
    adapter_id: str
    adapter_version: str
    implementation: str
    trust_ceiling: str
    supported_evidence_types: tuple[str, ...]
    execution_kind: str = "repo_python"


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


def _plugins_enabled() -> bool:
    return os.environ.get(PLUGIN_ENABLE_ENV, "").strip().lower() in {"1", "true", "yes"}


def _entry_points() -> tuple[importlib_metadata.EntryPoint, ...]:
    return tuple(importlib_metadata.entry_points().select(group=ENTRY_POINT_GROUP))


def _validate_spec(spec: TypedAdapterSpec, *, external: bool) -> list[str]:
    errors: list[str] = []
    if not _ADAPTER_ID_RE.fullmatch(spec.adapter_id):
        errors.append(f"invalid adapter_id {spec.adapter_id!r}")
    if not _SEMVER_RE.fullmatch(spec.adapter_version):
        errors.append(
            f"adapter {spec.adapter_id!r} has non-semver adapter_version "
            f"{spec.adapter_version!r}"
        )
    if spec.trust_ceiling not in TRUST_CLASS_RANK:
        errors.append(
            f"adapter {spec.adapter_id!r} has unknown trust ceiling {spec.trust_ceiling!r}"
        )
    if not spec.supported_evidence_types or any(
        not item for item in spec.supported_evidence_types
    ):
        errors.append(f"adapter {spec.adapter_id!r} has no valid supported evidence types")

    allowed_kind = "python_module" if external else "repo_python"
    if spec.execution_kind != allowed_kind:
        errors.append(
            f"adapter {spec.adapter_id!r} execution_kind must be {allowed_kind!r}, "
            f"got {spec.execution_kind!r}"
        )

    if external:
        if not _PYTHON_MODULE_RE.fullmatch(spec.implementation):
            errors.append(
                f"external adapter {spec.adapter_id!r} implementation must be a Python module, "
                f"got {spec.implementation!r}"
            )
        rank = TRUST_CLASS_RANK.get(spec.trust_ceiling)
        max_rank = TRUST_CLASS_RANK[MAX_EXTERNAL_PLUGIN_TRUST]
        if rank is not None and rank > max_rank:
            errors.append(
                f"external adapter {spec.adapter_id!r} trust ceiling {spec.trust_ceiling!r} "
                f"exceeds plugin maximum {MAX_EXTERNAL_PLUGIN_TRUST!r}"
            )
    else:
        implementation = spec.implementation.replace("\\", "/")
        if implementation.startswith("/") or ".." in implementation.split("/"):
            errors.append(
                f"built-in adapter {spec.adapter_id!r} has unsafe implementation path "
                f"{spec.implementation!r}"
            )
        if not implementation.endswith(".py"):
            errors.append(
                f"built-in adapter {spec.adapter_id!r} implementation must be a .py file"
            )
    return errors


def _builtin_registry_errors() -> list[str]:
    errors = [error for spec in _TYPED for error in _validate_spec(spec, external=False)]
    if len(TYPED_ADAPTERS) != len(_TYPED):
        errors.append("duplicate built-in typed adapter ids")

    for alias, adapter_id in sorted(LEGACY_TYPED_ADAPTER_ALIASES.items()):
        if adapter_id not in TYPED_ADAPTERS:
            errors.append(f"legacy alias {alias!r} targets unknown adapter {adapter_id!r}")

    for evidence_type, adapter_id in sorted(DEFAULT_TYPED_ADAPTER_BY_EVIDENCE_TYPE.items()):
        spec = TYPED_ADAPTERS.get(adapter_id)
        if spec is None:
            errors.append(
                f"default evidence type {evidence_type!r} targets unknown adapter {adapter_id!r}"
            )
        elif evidence_type not in spec.supported_evidence_types:
            errors.append(
                f"default adapter {adapter_id!r} does not support evidence type "
                f"{evidence_type!r}"
            )
    return errors


_BUILTIN_REGISTRY_ERRORS = _builtin_registry_errors()
if _BUILTIN_REGISTRY_ERRORS:  # pragma: no cover - import-time invariant
    raise AdapterRegistryError("; ".join(_BUILTIN_REGISTRY_ERRORS))


@lru_cache(maxsize=None)
def _load_external_adapter(adapter_id: str) -> TypedAdapterSpec | None:
    if not _plugins_enabled():
        return None
    matches = [ep for ep in _entry_points() if ep.name == adapter_id]
    if not matches:
        return None
    if len(matches) != 1:
        raise AdapterRegistryError(
            f"multiple {ENTRY_POINT_GROUP!r} entry points claim adapter id {adapter_id!r}"
        )
    if adapter_id in TYPED_ADAPTERS:
        raise AdapterRegistryError(
            f"external adapter {adapter_id!r} may not shadow a built-in adapter"
        )
    try:
        loaded = matches[0].load()
    except Exception as exc:
        raise AdapterRegistryError(
            f"external adapter {adapter_id!r} could not be loaded: {exc}"
        ) from exc
    if not isinstance(loaded, TypedAdapterSpec):
        raise AdapterRegistryError(
            f"entry point {adapter_id!r} must expose a TypedAdapterSpec constant"
        )
    if loaded.adapter_id != adapter_id:
        raise AdapterRegistryError(
            f"entry point name {adapter_id!r} does not match TypedAdapterSpec id "
            f"{loaded.adapter_id!r}"
        )
    errors = _validate_spec(loaded, external=True)
    if errors:
        raise AdapterRegistryError("; ".join(errors))
    return loaded


def clear_external_adapter_cache() -> None:
    """Clear lazy external-adapter discovery state, primarily for conformance tests."""
    _load_external_adapter.cache_clear()


def registered_typed_adapters(*, include_external: bool = False) -> dict[str, TypedAdapterSpec]:
    """Return built-ins and, when explicitly enabled, installed external adapters."""
    registry = dict(TYPED_ADAPTERS)
    if not include_external or not _plugins_enabled():
        return registry
    for adapter_id in sorted({ep.name for ep in _entry_points()}):
        if adapter_id in registry:
            raise AdapterRegistryError(
                f"external adapter {adapter_id!r} may not shadow a built-in adapter"
            )
        spec = _load_external_adapter(adapter_id)
        if spec is not None:
            registry[adapter_id] = spec
    return registry


def get_typed_adapter(adapter_id: str) -> TypedAdapterSpec | None:
    """Resolve an exact typed adapter id; legacy aliases are intentionally not accepted."""
    builtin = TYPED_ADAPTERS.get(adapter_id)
    if builtin is not None:
        return builtin
    return _load_external_adapter(adapter_id)


def resolve_typed_adapter_identity(
    adapter_identity: str,
    evidence_type: str | None = None,
) -> TypedAdapterSpec | None:
    """Resolve an exact typed id or a historical spec alias to one typed identity."""
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
    adapter_id: str,
    adapter_version: str,
    evidence_type: str | None = None,
) -> list[str]:
    try:
        spec = get_typed_adapter(adapter_id)
    except AdapterRegistryError as exc:
        return [str(exc)]
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

"""Resource bounds for dense-matrix and related backends."""

from __future__ import annotations

import os

DEFAULT_MAX_DENSE_QUBITS = 8
# Permutation state vectors are still 2^n; keep a hard ceiling for accidental large n.
DEFAULT_MAX_PERM_QUBITS = 24

DENSE_DISABLED_MSG = (
    "dense matrix backend disabled for {n} qubits; select a scalable adapter"
)
PERM_DISABLED_MSG = (
    "permutation backend disabled for {n} qubits; raise QSPECBENCH_MAX_PERM_QUBITS "
    "or use certificate_only/qcec"
)


def max_dense_qubits() -> int:
    """Conservative default; override with QSPECBENCH_MAX_DENSE_QUBITS."""
    raw = os.environ.get("QSPECBENCH_MAX_DENSE_QUBITS", "").strip()
    if not raw:
        return DEFAULT_MAX_DENSE_QUBITS
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(
            f"QSPECBENCH_MAX_DENSE_QUBITS must be a positive integer, got {raw!r}"
        ) from exc
    if value < 1:
        raise ValueError(f"QSPECBENCH_MAX_DENSE_QUBITS must be >= 1, got {value}")
    return value


def max_perm_qubits() -> int:
    """Hard ceiling for permutation backends; override with QSPECBENCH_MAX_PERM_QUBITS."""
    raw = os.environ.get("QSPECBENCH_MAX_PERM_QUBITS", "").strip()
    if not raw:
        return DEFAULT_MAX_PERM_QUBITS
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(
            f"QSPECBENCH_MAX_PERM_QUBITS must be a positive integer, got {raw!r}"
        ) from exc
    if value < 1:
        raise ValueError(f"QSPECBENCH_MAX_PERM_QUBITS must be >= 1, got {value}")
    return value


def dense_matrix_allowed(n_qubits: int) -> bool:
    return n_qubits <= max_dense_qubits()


def perm_circuit_allowed(n_qubits: int) -> bool:
    return n_qubits <= max_perm_qubits()


def require_dense_matrix(n_qubits: int) -> None:
    """Fail-closed gate before allocating a 2^n × 2^n dense unitary."""
    if not dense_matrix_allowed(n_qubits):
        raise ValueError(DENSE_DISABLED_MSG.format(n=n_qubits))


def require_perm_circuit(n_qubits: int) -> None:
    """Fail-closed gate before allocating a 2^n permutation / state table."""
    if not perm_circuit_allowed(n_qubits):
        raise ValueError(PERM_DISABLED_MSG.format(n=n_qubits))

"""Python mirror of `QSpecBench.Quantum.OpenQASM3` denotation (integer scaffold)."""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from qspecbench.qasm_matrix import _apply_single, _cnot, _eye, _mat_mul, _single_qubit_gate


def denotate_gate(name: str) -> list[list[Fraction]]:
    return _single_qubit_gate(name)


def denotate_ops(n_qubits: int, ops: list[tuple[str, tuple[int, ...]]]) -> list[list[Fraction]]:
    """Denotate a gate list with the same left-multiply order as qasm_matrix."""
    unitary = _eye(1 << n_qubits)
    for gate, args in ops:
        g = gate.lower()
        if g in {"cx", "cnot"}:
            op = _cnot(n_qubits, args[0], args[1])
        else:
            op = _apply_single(n_qubits, g, args[0])
        unitary = _mat_mul(op, unitary)
    return unitary


def ops_from_qasm_matrix(data: dict[str, Any]) -> list[tuple[str, tuple[int, ...]]]:
    import re

    ops: list[tuple[str, tuple[int, ...]]] = []
    for line in data.get("gates_applied", []):
        stripped = line.strip().rstrip(";")
        if not stripped:
            continue
        parts = stripped.split(None, 1)
        gate = parts[0].lower()
        if gate not in {"i", "x", "y", "z", "h", "s", "t", "cx", "cnot"}:
            continue
        arg_text = parts[1] if len(parts) > 1 else ""
        args = [int(m.group(1)) for m in re.finditer(r"\[(\d+)\]", arg_text)]
        if gate in {"cx", "cnot"}:
            if len(args) != 2:
                raise ValueError(f"CX expects two qubit indices: {line}")
        elif len(args) != 1:
            raise ValueError(f"single-qubit gate expects one qubit index: {line}")
        ops.append((gate, tuple(args)))
    return ops


def matrices_equal(a: list[list[Fraction]], b: list[list[Fraction]]) -> bool:
    return all(x == y for row_a, row_b in zip(a, b) for x, y in zip(row_a, row_b))

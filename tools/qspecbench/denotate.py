"""Python mirror of `QSpecBench.Quantum.OpenQASM3` denotation."""

from __future__ import annotations

import re
from typing import Any

from qspecbench.qasm_matrix import (
    ComplexMatrix,
    _apply_rx,
    _apply_single,
    _ccx,
    _cnot,
    _cp,
    _eye,
    _mat_mul,
    _parse_qubit_index,
    _swap,
    matrices_equal,
    matrix_from_json_rows,
)

Op = tuple[str, tuple[int, ...], float | None]


def denotate_ops(n_qubits: int, ops: list[Op]) -> ComplexMatrix:
    """Denotate a gate list with the same left-multiply order as qasm_matrix."""
    unitary = _eye(1 << n_qubits)
    for gate, args, angle in ops:
        g = gate.lower()
        if g == "rx":
            if angle is None:
                raise ValueError("rx gate requires angle")
            op = _apply_rx(n_qubits, angle, args[0])
        elif g in {"cx", "cnot"}:
            op = _cnot(n_qubits, args[0], args[1])
        elif g == "ccx":
            op = _ccx(n_qubits, args[0], args[1], args[2])
        elif g == "swap":
            op = _swap(n_qubits, args[0], args[1])
        elif g == "cp":
            if angle is None:
                raise ValueError("cp gate requires angle")
            op = _cp(n_qubits, args[0], args[1], angle)
        else:
            op = _apply_single(n_qubits, g, args[0])
        unitary = _mat_mul(op, unitary)
    return unitary


def ops_from_qasm_matrix(data: dict[str, Any]) -> list[Op]:
    n = data["n_qubits"]
    ops: list[Op] = []
    for line in data.get("gates_applied", []):
        stripped = line.strip().rstrip(";")
        if not stripped:
            continue
        rx = re.match(r"^\s*rx\s*\(\s*([0-9.eE+-]+)\s*\)\s+(q\[\d+\]|q\d+)\s*;?\s*$", stripped, re.I)
        if rx:
            angle = float(rx.group(1))
            q = _parse_qubit_index(rx.group(2), n)
            ops.append(("rx", (q,), angle))
            continue
        cp = re.match(r"^\s*cp\s*\(\s*([0-9.eE+-]+)\s*\)\s+(.*);?\s*$", stripped, re.I)
        if cp:
            angle = float(cp.group(1))
            args = tuple(int(m.group(1)) for m in re.finditer(r"\[(\d+)\]", cp.group(2)))
            if len(args) != 2:
                raise ValueError(f"CP expects two qubit indices: {line}")
            ops.append(("cp", args, angle))
            continue
        parts = stripped.split(None, 1)
        gate = parts[0].lower()
        supported = {"i", "x", "y", "z", "h", "s", "t", "sdg", "tdg", "cx", "cnot", "ccx", "swap"}
        if gate not in supported:
            continue
        arg_text = parts[1] if len(parts) > 1 else ""
        args = tuple(int(m.group(1)) for m in re.finditer(r"\[(\d+)\]", arg_text))
        if gate in {"cx", "cnot"}:
            if len(args) != 2:
                raise ValueError(f"CX expects two qubit indices: {line}")
        elif gate == "ccx":
            if len(args) != 3:
                raise ValueError(f"CCX expects three qubit indices: {line}")
        elif gate == "swap":
            if len(args) != 2:
                raise ValueError(f"SWAP expects two qubit indices: {line}")
        elif len(args) != 1:
            raise ValueError(f"single-qubit gate expects one qubit index: {line}")
        ops.append((gate, args, None))
    return ops


def matrix_from_qasm_json(data: dict[str, Any]) -> ComplexMatrix:
    return matrix_from_json_rows(data["matrix"])


__all__ = [
    "ComplexMatrix",
    "Op",
    "denotate_ops",
    "matrices_equal",
    "matrix_from_qasm_json",
    "ops_from_qasm_matrix",
]

"""Canonical little-endian unitary semantics for the QSpecBench OpenQASM subset.

This module intentionally does not replace :mod:`qspecbench.qasm_matrix`. The latter
is retained for historical evidence whose hashes were produced under the legacy
matrix path. New promotable Python unitary evidence should use
``extract_lsb_unitary`` and the ``qspecbench.openqasm3.unitary_lsb.v2`` profile.

The canonical convention is explicit: OpenQASM wire ``q[i]`` is bit weight ``2**i``
in the basis-state index. Hadamard is normalized by a deterministic rational
approximation to ``1/sqrt(2)``. Unsupported syntax fails closed.
"""

from __future__ import annotations

import re
from fractions import Fraction
from pathlib import Path
from typing import Any

from qspecbench.qasm_matrix import (
    ComplexMatrix,
    UnsupportedQasmError,
    _CP_LINE,
    _GATE_LINE,
    _RX_LINE,
    _RY_LINE,
    _RZ_LINE,
    _SQRT2_HALF,
    _U_LINE,
    _ccx,
    _cnot,
    _cp,
    _cz,
    _eye,
    _kron,
    _line_skip_category,
    _mat_mul,
    _parse_angle,
    _parse_angle_list,
    _parse_qubit_args,
    _parse_qubit_index,
    _register_size,
    _rx_matrix,
    _ry_matrix,
    _rz_matrix,
    _single_qubit_gate,
    _swap,
    _u_matrix,
    cell_to_json,
)
from qspecbench.resource_bounds import require_dense_matrix

CANONICAL_WIRE_ORDER = "openqasm_little_endian_wire_order"
CANONICAL_GATE_SET: frozenset[str] = frozenset(
    {
        "h",
        "x",
        "y",
        "z",
        "s",
        "sdg",
        "t",
        "tdg",
        "cx",
        "cnot",
        "cz",
        "swap",
        "ccx",
        "rx",
        "ry",
        "rz",
        "u",
        "cp",
    }
)
_HEADER = "OPENQASM 3.0"
_QUBIT_DECL = re.compile(r"^qubit\s*\[\s*(\d+)\s*\]\s+q\s*;?$")


def _clean_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.split("//", 1)[0].strip()
        if line:
            lines.append(line)
    return lines


def _validate_header(lines: list[str]) -> None:
    headers = [
        line.rstrip(";").strip()
        for line in lines
        if line.lower().startswith("openqasm")
    ]
    if headers != [_HEADER]:
        raise UnsupportedQasmError(
            "canonical unitary profile requires exactly one 'OPENQASM 3.0;' header; "
            f"found {headers!r}"
        )


def _scale_matrix(matrix: ComplexMatrix, factor: Fraction) -> ComplexMatrix:
    return [[(re * factor, im * factor) for re, im in row] for row in matrix]


def embed_single_lsb(n_qubits: int, qubit: int, op: ComplexMatrix) -> ComplexMatrix:
    """Embed a 2x2 operator with ``q[i]`` equal to basis-index bit ``i``.

    The right-most Kronecker factor is therefore wire ``q[0]``. This convention is
    consistent with the permutation implementations of CX/CCX/SWAP in
    :mod:`qspecbench.qasm_matrix` and with the operational dynamic simulator.
    """
    if qubit < 0 or qubit >= n_qubits:
        raise ValueError(f"qubit index {qubit} out of range for {n_qubits} qubits")
    factors = [op if q == qubit else _eye(2) for q in range(n_qubits)]
    result = factors[0]
    for factor in factors[1:]:
        result = _kron(factor, result)
    return result


def _single_gate_lsb(n_qubits: int, gate: str, qubit: int) -> ComplexMatrix:
    op = _single_qubit_gate(gate)
    if gate.lower() == "h":
        op = _scale_matrix(op, _SQRT2_HALF)
    return embed_single_lsb(n_qubits, qubit, op)


def gate_matrix_lsb(n_qubits: int, line: str) -> ComplexMatrix:
    """Interpret one supported OpenQASM gate line under canonical LSB semantics."""
    rx = _RX_LINE.match(line)
    if rx:
        q = _parse_qubit_index(rx.group(2), n_qubits)
        return embed_single_lsb(n_qubits, q, _rx_matrix(_parse_angle(rx.group(1))))

    ry = _RY_LINE.match(line)
    if ry:
        q = _parse_qubit_index(ry.group(2), n_qubits)
        return embed_single_lsb(n_qubits, q, _ry_matrix(_parse_angle(ry.group(1))))

    rz = _RZ_LINE.match(line)
    if rz:
        q = _parse_qubit_index(rz.group(2), n_qubits)
        return embed_single_lsb(n_qubits, q, _rz_matrix(_parse_angle(rz.group(1))))

    u = _U_LINE.match(line)
    if u:
        angles = _parse_angle_list(u.group(1))
        if len(angles) != 3:
            raise ValueError(f"U expects three angles: {line}")
        q = _parse_qubit_index(u.group(2), n_qubits)
        return embed_single_lsb(
            n_qubits,
            q,
            _u_matrix(angles[0], angles[1], angles[2]),
        )

    cp = _CP_LINE.match(line)
    if cp:
        args = _parse_qubit_args(cp.group(2), n_qubits)
        if len(args) != 2:
            raise ValueError(f"CP expects two qubit arguments: {line}")
        return _cp(n_qubits, args[0], args[1], _parse_angle(cp.group(1)))

    match = _GATE_LINE.match(line)
    if not match:
        raise UnsupportedQasmError(
            f"unsupported QASM gate under canonical LSB semantics: {line!r}"
        )

    gate = match.group(1).lower()
    args = _parse_qubit_args(match.group(2), n_qubits)
    if gate in {"cx", "cnot"}:
        if len(args) != 2:
            raise ValueError(f"CX expects two arguments: {line}")
        return _cnot(n_qubits, args[0], args[1])
    if gate == "ccx":
        if len(args) != 3:
            raise ValueError(f"CCX expects three arguments: {line}")
        return _ccx(n_qubits, args[0], args[1], args[2])
    if gate == "swap":
        if len(args) != 2:
            raise ValueError(f"SWAP expects two arguments: {line}")
        return _swap(n_qubits, args[0], args[1])
    if gate == "cz":
        if len(args) != 2:
            raise ValueError(f"CZ expects two arguments: {line}")
        return _cz(n_qubits, args[0], args[1])
    if len(args) != 1:
        raise ValueError(f"single-qubit gate expects one argument: {line}")
    return _single_gate_lsb(n_qubits, gate, args[0])


def extract_lsb_unitary(qasm_path: Path) -> dict[str, Any]:
    """Extract a normalized unitary under the canonical little-endian profile.

    Only the exact OpenQASM 3.0 header, one ``qubit[n] q`` declaration, documented
    gate subset, and restricted angle grammar are accepted. Include statements are
    skipped but not interpreted as library imports. All other syntax fails closed.
    """
    text = qasm_path.read_text(encoding="utf-8")
    lines = _clean_lines(text)
    _validate_header(lines)
    n_qubits = _register_size(text)
    require_dense_matrix(n_qubits)
    unitary = _eye(1 << n_qubits)
    gates_applied: list[str] = []
    seen_qubit_declaration = False

    for line in lines:
        lower = line.lower()
        if lower.startswith("openqasm"):
            continue
        if lower.startswith("include"):
            continue

        category = _line_skip_category(line)
        if category == "declaration":
            declaration = _QUBIT_DECL.fullmatch(line)
            if declaration is None:
                raise UnsupportedQasmError(
                    "canonical unitary profile requires declaration 'qubit[n] q;'; "
                    f"got {line!r}"
                )
            if seen_qubit_declaration:
                raise UnsupportedQasmError(
                    "canonical unitary profile permits exactly one qubit register q"
                )
            declared_qubits = int(declaration.group(1))
            if declared_qubits != n_qubits:
                raise UnsupportedQasmError("inconsistent qubit register declaration")
            seen_qubit_declaration = True
            continue
        if category is not None:
            raise UnsupportedQasmError(
                f"canonical unitary profile does not interpret {category!r}: {line!r}"
            )

        op = gate_matrix_lsb(n_qubits, line)
        unitary = _mat_mul(op, unitary)
        gates_applied.append(line)

    if not seen_qubit_declaration:
        raise UnsupportedQasmError(
            "canonical unitary profile requires declaration 'qubit[n] q;'"
        )

    return {
        "source": str(qasm_path),
        "n_qubits": n_qubits,
        "gate_model": "openqasm3_complex_unitary_normalized_lsb_v2",
        "wire_order": CANONICAL_WIRE_ORDER,
        "global_phase_policy": "exact",
        "numeric_semantics": "Fraction-based rational approximation",
        "gates_applied": gates_applied,
        "matrix": [
            [cell_to_json(unitary[i][j]) for j in range(len(unitary))]
            for i in range(len(unitary))
        ],
    }

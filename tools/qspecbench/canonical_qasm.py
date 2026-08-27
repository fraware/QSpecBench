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

import math
import re
from fractions import Fraction
from pathlib import Path
from typing import Any

from qspecbench.qasm_matrix import (
    ComplexMatrix,
    UnsupportedQasmError,
    _SQRT2_HALF,
    _ccx,
    _cell,
    _cnot,
    _eye,
    _kron,
    _line_skip_category,
    _mat_mul,
    _parse_angle,
    _parse_qubit_index,
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
_HEADER = "OPENQASM 3.0;"
_QREF = r"(q\[\d+\])"
_ANGLE_ARG = r"([^)]+)"
_QUBIT_DECL = re.compile(r"^qubit\s*\[\s*(\d+)\s*\]\s+q\s*;$")
_INCLUDE_LINE = re.compile(r'^include\s+"[^"\r\n]+"\s*;$')
_SINGLE_GATE_LINE = re.compile(
    rf"^\s*(h|x|y|z|s|t|sdg|tdg)\s+{_QREF}\s*;\s*$"
)
_TWO_GATE_LINE = re.compile(
    rf"^\s*(cx|cnot|cz|swap)\s+{_QREF}\s*,\s*{_QREF}\s*;\s*$"
)
_CCX_LINE = re.compile(
    rf"^\s*ccx\s+{_QREF}\s*,\s*{_QREF}\s*,\s*{_QREF}\s*;\s*$"
)
_RX_LINE_STRICT = re.compile(
    rf"^\s*rx\s*\(\s*{_ANGLE_ARG}\s*\)\s+{_QREF}\s*;\s*$"
)
_RY_LINE_STRICT = re.compile(
    rf"^\s*ry\s*\(\s*{_ANGLE_ARG}\s*\)\s+{_QREF}\s*;\s*$"
)
_RZ_LINE_STRICT = re.compile(
    rf"^\s*rz\s*\(\s*{_ANGLE_ARG}\s*\)\s+{_QREF}\s*;\s*$"
)
_U_LINE_STRICT = re.compile(
    rf"^\s*u\s*\(\s*([^)]+)\s*\)\s+{_QREF}\s*;\s*$"
)
_CP_LINE_STRICT = re.compile(
    rf"^\s*cp\s*\(\s*{_ANGLE_ARG}\s*\)\s+{_QREF}\s*,\s*{_QREF}\s*;\s*$"
)


def _clean_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.split("//", 1)[0].strip()
        if line:
            lines.append(line)
    return lines


def _validate_header(lines: list[str]) -> None:
    headers = [line for line in lines if line.lower().startswith("openqasm")]
    if not lines or lines[0] != _HEADER or headers != [_HEADER]:
        raise UnsupportedQasmError(
            "canonical unitary profile requires exactly one leading 'OPENQASM 3.0;' "
            f"header; found {headers!r}"
        )


def _declared_qubit_count(lines: list[str]) -> int:
    declarations = [
        match
        for line in lines
        if (match := _QUBIT_DECL.fullmatch(line)) is not None
    ]
    if len(declarations) != 1:
        raise UnsupportedQasmError(
            "canonical unitary profile requires exactly one declaration 'qubit[n] q;'"
        )
    n_qubits = int(declarations[0].group(1))
    if n_qubits <= 0:
        raise UnsupportedQasmError("qubit register width must be positive")
    return n_qubits


def _scale_matrix(matrix: ComplexMatrix, factor: Fraction) -> ComplexMatrix:
    return [[(re_part * factor, im_part * factor) for re_part, im_part in row] for row in matrix]


def embed_single_lsb(n_qubits: int, qubit: int, op: ComplexMatrix) -> ComplexMatrix:
    """Embed a 2x2 operator with ``q[i]`` equal to basis-index bit ``i``.

    The right-most Kronecker factor is therefore wire ``q[0]``. This convention is
    consistent with the permutation implementations of CX/CCX/SWAP in the legacy
    module and with the v2 operational dynamic interpreter.
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
    if gate == "h":
        op = _scale_matrix(op, _SQRT2_HALF)
    return embed_single_lsb(n_qubits, qubit, op)


def _require_distinct(gate: str, qubits: tuple[int, ...]) -> None:
    if len(set(qubits)) != len(qubits):
        raise UnsupportedQasmError(
            f"{gate.upper()} requires distinct qubit operands, got {qubits}"
        )


def _controlled_phase_lsb(
    n_qubits: int,
    control: int,
    target: int,
    theta: float,
) -> ComplexMatrix:
    """Controlled phase on every basis state where both selected LSB wires are 1."""
    _require_distinct("cp", (control, target))
    dim = 1 << n_qubits
    result = _eye(dim)
    phase = _cell(
        Fraction(math.cos(theta)).limit_denominator(10**12),
        Fraction(math.sin(theta)).limit_denominator(10**12),
    )
    for index in range(dim):
        if ((index >> control) & 1) and ((index >> target) & 1):
            result[index][index] = phase
    return result


def _cz_lsb(n_qubits: int, control: int, target: int) -> ComplexMatrix:
    """CZ on every basis state where both selected LSB wires are 1."""
    _require_distinct("cz", (control, target))
    dim = 1 << n_qubits
    result = _eye(dim)
    for index in range(dim):
        if ((index >> control) & 1) and ((index >> target) & 1):
            result[index][index] = _cell(-1)
    return result


def _parse_u_angles(text: str) -> tuple[float, float, float]:
    parts = [part.strip() for part in text.split(",")]
    if len(parts) != 3 or any(not part for part in parts):
        raise UnsupportedQasmError(f"U expects exactly three non-empty angles: {text!r}")
    return (_parse_angle(parts[0]), _parse_angle(parts[1]), _parse_angle(parts[2]))


def gate_matrix_lsb(n_qubits: int, line: str) -> ComplexMatrix:
    """Interpret one supported gate statement under canonical LSB semantics."""
    rx = _RX_LINE_STRICT.fullmatch(line)
    if rx:
        q = _parse_qubit_index(rx.group(2), n_qubits)
        return embed_single_lsb(n_qubits, q, _rx_matrix(_parse_angle(rx.group(1))))

    ry = _RY_LINE_STRICT.fullmatch(line)
    if ry:
        q = _parse_qubit_index(ry.group(2), n_qubits)
        return embed_single_lsb(n_qubits, q, _ry_matrix(_parse_angle(ry.group(1))))

    rz = _RZ_LINE_STRICT.fullmatch(line)
    if rz:
        q = _parse_qubit_index(rz.group(2), n_qubits)
        return embed_single_lsb(n_qubits, q, _rz_matrix(_parse_angle(rz.group(1))))

    u = _U_LINE_STRICT.fullmatch(line)
    if u:
        theta, phi, lam = _parse_u_angles(u.group(1))
        q = _parse_qubit_index(u.group(2), n_qubits)
        return embed_single_lsb(n_qubits, q, _u_matrix(theta, phi, lam))

    cp = _CP_LINE_STRICT.fullmatch(line)
    if cp:
        control = _parse_qubit_index(cp.group(2), n_qubits)
        target = _parse_qubit_index(cp.group(3), n_qubits)
        return _controlled_phase_lsb(
            n_qubits,
            control,
            target,
            _parse_angle(cp.group(1)),
        )

    ccx = _CCX_LINE.fullmatch(line)
    if ccx:
        c1 = _parse_qubit_index(ccx.group(1), n_qubits)
        c2 = _parse_qubit_index(ccx.group(2), n_qubits)
        target = _parse_qubit_index(ccx.group(3), n_qubits)
        _require_distinct("ccx", (c1, c2, target))
        return _ccx(n_qubits, c1, c2, target)

    two = _TWO_GATE_LINE.fullmatch(line)
    if two:
        gate = two.group(1)
        first = _parse_qubit_index(two.group(2), n_qubits)
        second = _parse_qubit_index(two.group(3), n_qubits)
        _require_distinct(gate, (first, second))
        if gate in {"cx", "cnot"}:
            return _cnot(n_qubits, first, second)
        if gate == "swap":
            return _swap(n_qubits, first, second)
        if gate == "cz":
            return _cz_lsb(n_qubits, first, second)
        raise AssertionError(f"unreachable two-qubit gate {gate!r}")

    single = _SINGLE_GATE_LINE.fullmatch(line)
    if single:
        gate = single.group(1)
        qubit = _parse_qubit_index(single.group(2), n_qubits)
        return _single_gate_lsb(n_qubits, gate, qubit)

    raise UnsupportedQasmError(
        f"unsupported or malformed QASM gate under canonical LSB semantics: {line!r}"
    )


def extract_lsb_unitary(qasm_path: Path) -> dict[str, Any]:
    """Extract a normalized unitary under the canonical little-endian profile.

    Only the exact leading ``OPENQASM 3.0;`` header, one terminated ``qubit[n] q;``
    declaration, documented gate subset, and restricted angle grammar are accepted.
    Syntactically valid include statements are skipped but not interpreted as library
    imports. All other syntax fails closed.
    """
    text = qasm_path.read_text(encoding="utf-8")
    lines = _clean_lines(text)
    _validate_header(lines)
    n_qubits = _declared_qubit_count(lines)
    require_dense_matrix(n_qubits)
    unitary = _eye(1 << n_qubits)
    gates_applied: list[str] = []

    for line in lines:
        lower = line.lower()
        if line == _HEADER:
            continue
        if lower.startswith("include"):
            if _INCLUDE_LINE.fullmatch(line) is None:
                raise UnsupportedQasmError(
                    f"malformed include statement under canonical unitary profile: {line!r}"
                )
            continue

        category = _line_skip_category(line)
        if category == "declaration":
            if _QUBIT_DECL.fullmatch(line) is None:
                raise UnsupportedQasmError(
                    "canonical unitary profile requires declaration 'qubit[n] q;'; "
                    f"got {line!r}"
                )
            continue
        if category is not None:
            raise UnsupportedQasmError(
                f"canonical unitary profile does not interpret {category!r}: {line!r}"
            )

        op = gate_matrix_lsb(n_qubits, line)
        unitary = _mat_mul(op, unitary)
        gates_applied.append(line)

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

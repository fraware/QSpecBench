"""Extract unitary matrices from a restricted OpenQASM 3 gate subset."""

from __future__ import annotations

import json
import re
from fractions import Fraction
from pathlib import Path
from typing import Any

_GATE_LINE = re.compile(
    r"^\s*(h|x|y|z|s|t|sdg|tdg|cx|cnot|swap)\s+(.*);?\s*$",
    re.IGNORECASE,
)
_RX_LINE = re.compile(
    r"^\s*rx\s*\(\s*([0-9.eE+-]+)\s*\)\s+(q\[\d+\]|q\d+)\s*;?\s*$",
    re.IGNORECASE,
)


def _eye(n: int) -> list[list[Fraction]]:
    return [[Fraction(1 if i == j else 0) for j in range(n)] for i in range(n)]


def _single_qubit_gate(name: str) -> list[list[Fraction]]:
    g = name.lower()
    if g == "h":
        return [[Fraction(1), Fraction(1)], [Fraction(1), Fraction(-1)]]
    if g == "x":
        return [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
    if g == "y":
        return [[Fraction(0), Fraction(-1)], [Fraction(1), Fraction(0)]]
    if g == "z":
        return [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(-1)]]
    if g in {"s", "t", "sdg", "tdg"}:
        return _eye(2)
    raise ValueError(f"unsupported single-qubit gate: {name}")


def _mat_mul(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    n = len(a)
    return [
        [sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n)]
        for i in range(n)
    ]


def _kron(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    ra, ca = len(a), len(a[0])
    rb, cb = len(b), len(b[0])
    return [
        [a[i // rb][j // cb] * b[i % rb][j % cb] for j in range(ca * cb)]
        for i in range(ra * rb)
    ]


def _apply_single(n_qubits: int, gate: str, qubit: int) -> list[list[Fraction]]:
    op = _single_qubit_gate(gate)
    mats: list[list[list[Fraction]]] = []
    for q in range(n_qubits):
        mats.append(op if q == qubit else _eye(2))
    result = mats[0]
    for m in mats[1:]:
        result = _kron(result, m)
    return result


def _cnot(n_qubits: int, control: int, target: int) -> list[list[Fraction]]:
    dim = 1 << n_qubits
    result = _eye(dim)
    for row in range(dim):
        bits = [(row >> q) & 1 for q in range(n_qubits)]
        col_bits = list(bits)
        if bits[control] == 1:
            col_bits[target] ^= 1
        col = sum(col_bits[q] << q for q in range(n_qubits))
        for c in range(dim):
            result[row][c] = Fraction(1 if c == col else 0)
    return result


def _swap(n_qubits: int, a: int, b: int) -> list[list[Fraction]]:
    dim = 1 << n_qubits
    result = _eye(dim)
    for row in range(dim):
        bits = [(row >> q) & 1 for q in range(n_qubits)]
        col_bits = list(bits)
        if bits[a] != bits[b]:
            col_bits[a], col_bits[b] = col_bits[b], col_bits[a]
        col = sum(col_bits[q] << q for q in range(n_qubits))
        for c in range(dim):
            result[row][c] = Fraction(1 if c == col else 0)
    return result


def _parse_qubit_index(token: str, n_qubits: int) -> int:
    m = re.search(r"\[(\d+)\]", token)
    if m:
        idx = int(m.group(1))
    else:
        m2 = re.search(r"q(\d+)", token.lower())
        if not m2:
            raise ValueError(f"cannot parse qubit index from {token}")
        idx = int(m2.group(1))
    if idx < 0 or idx >= n_qubits:
        raise ValueError(f"qubit index {idx} out of range for {n_qubits} qubits")
    return idx


def _parse_qubit_args(rest: str, n_qubits: int) -> list[int]:
    args: list[int] = []
    for token in rest.replace(",", " ").split():
        if "q" in token.lower():
            args.append(_parse_qubit_index(token, n_qubits))
    return args


def _register_size(text: str) -> int:
    m = re.search(r"qubit\s*\[\s*(\d+)\s*\]", text)
    if not m:
        raise ValueError("expected qubit[n] register declaration")
    return int(m.group(1))


def extract_matrix(qasm_path: Path) -> dict[str, Any]:
    text = qasm_path.read_text(encoding="utf-8")
    n = _register_size(text)
    unitary = _eye(1 << n)
    gates_applied: list[str] = []

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("//") or line.lower().startswith("openqasm"):
            continue
        if line.lower().startswith("include"):
            continue

        rx = _RX_LINE.match(line)
        if rx:
            angle = float(rx.group(1))
            q = _parse_qubit_index(rx.group(2), n)
            if abs(angle - 1.57079632679) < 1e-6:
                op = _apply_single(n, "h", q)
            else:
                raise ValueError(f"unsupported rx angle: {angle}")
            unitary = _mat_mul(op, unitary)
            gates_applied.append(line)
            continue

        m = _GATE_LINE.match(line)
        if not m:
            continue
        gate = m.group(1).lower()
        args = _parse_qubit_args(m.group(2), n)
        if gate in {"cx", "cnot"}:
            if len(args) != 2:
                raise ValueError(f"CX expects two arguments: {line}")
            op = _cnot(n, args[0], args[1])
        elif gate == "swap":
            if len(args) != 2:
                raise ValueError(f"SWAP expects two arguments: {line}")
            op = _swap(n, args[0], args[1])
        else:
            if len(args) != 1:
                raise ValueError(f"single-qubit gate expects one argument: {line}")
            op = _apply_single(n, gate, args[0])
        unitary = _mat_mul(op, unitary)
        gates_applied.append(line)

    gate_trace: list[dict[str, Any]] = []
    for line in gates_applied:
        stripped = line.strip().rstrip(";")
        parts = stripped.split()
        gate = parts[0].lower()
        if gate.startswith("rx"):
            args = [_parse_qubit_index(parts[-1], n)]
        else:
            args = _parse_qubit_args(" ".join(parts[1:]), n)
        gate_trace.append({"gate": gate, "args": args})

    def frac_cell(x: Fraction) -> list[int]:
        return [x.numerator, x.denominator]

    return {
        "source": str(qasm_path),
        "n_qubits": n,
        "gate_model": "openqasm3_1q2q_clifford",
        "normalization": {
            "hadamard": "unnormalized_int_model",
            "qasm_factor": "1/sqrt(2) per gate",
        },
        "gates_applied": gates_applied,
        "gate_trace": gate_trace,
        "matrix": [
            [frac_cell(unitary[i][j]) for j in range(len(unitary))]
            for i in range(len(unitary))
        ],
    }


def write_matrix(qasm_path: Path, out_path: Path) -> dict[str, Any]:
    data = extract_matrix(qasm_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data

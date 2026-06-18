"""Extract small-gate-set unitary matrices from OpenQASM 3 circuits."""

from __future__ import annotations

import json
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

GATE_RE = re.compile(
    r"^\s*(?P<gate>[a-z]+)\s+(?P<args>[^;]+);",
    re.IGNORECASE | re.MULTILINE,
)


def _eye(n: int) -> list[list[Fraction]]:
    return [[Fraction(int(i == j), 1) for j in range(n)] for i in range(n)]


def _mat_mul(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    n = len(a)
    return [
        [sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n)]
        for i in range(n)
    ]


def _kron(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    ra, ca = len(a), len(a[0])
    rb, cb = len(b), len(b[0])
    out = [[Fraction(0) for _ in range(ca * cb)] for _ in range(ra * rb)]
    for i in range(ra):
        for j in range(ca):
            for k in range(rb):
                for l in range(cb):
                    out[i * rb + k][j * cb + l] = a[i][j] * b[k][l]
    return out


def _single_qubit_gate(name: str) -> list[list[Fraction]]:
    gates = {
        "i": _eye(2),
        "x": [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]],
        "y": [[Fraction(0), Fraction(-1)], [Fraction(1), Fraction(0)]],
        "z": [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(-1)]],
        "h": [[Fraction(1), Fraction(1)], [Fraction(1), Fraction(-1)]],
        "s": [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]],  # phase i omitted; integer scaffold
        "t": [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]],
    }
    key = name.lower()
    if key not in gates:
        raise ValueError(f"unsupported gate: {name}")
    return gates[key]


def _cnot(n: int, control: int, target: int) -> list[list[Fraction]]:
    mat = _eye(1 << n)
    dim = 1 << n
    for col in range(dim):
        bits = [(col >> q) & 1 for q in range(n)]
        if bits[control] == 1:
            flipped = col ^ (1 << target)
            if col < flipped:
                mat[col][col] = Fraction(0)
                mat[flipped][col] = Fraction(1)
            elif col > flipped:
                mat[col][col] = Fraction(0)
                mat[flipped][col] = Fraction(1)
    return mat


def _apply_single(n: int, gate: str, qubit: int) -> list[list[Fraction]]:
    ops = [_eye(2) if q != qubit else _single_qubit_gate(gate) for q in range(n)]
    result = ops[0]
    for op in ops[1:]:
        result = _kron(result, op)
    return result


def _parse_qubit_index(arg: str, n: int) -> int:
    m = re.search(r"\[(\d+)\]", arg)
    if not m:
        raise ValueError(f"cannot parse qubit index from {arg}")
    idx = int(m.group(1))
    if idx < 0 or idx >= n:
        raise ValueError(f"qubit index {idx} out of range for n={n}")
    return idx


def extract_matrix(qasm_path: Path) -> dict[str, Any]:
    text = qasm_path.read_text(encoding="utf-8")
    n_match = re.search(r"qubit\[(\d+)\]", text)
    if not n_match:
        raise ValueError("qubit register declaration not found")
    n = int(n_match.group(1))
    unitary = _eye(1 << n)
    gates_applied: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        if stripped.startswith("OPENQASM") or stripped.startswith("include") or stripped.startswith("qubit"):
            continue
        m = GATE_RE.match(stripped)
        if not m:
            continue
        gate = m.group("gate").lower()
        args = [a.strip() for a in m.group("args").split(",")]
        if gate == "cx" or gate == "cnot":
            if len(args) != 2:
                raise ValueError(f"CX expects two arguments: {stripped}")
            c = _parse_qubit_index(args[0], n)
            t = _parse_qubit_index(args[1], n)
            op = _cnot(n, c, t)
        else:
            if len(args) != 1:
                raise ValueError(f"single-qubit gate expects one argument: {stripped}")
            q = _parse_qubit_index(args[0], n)
            op = _apply_single(n, gate, q)
        unitary = _mat_mul(op, unitary)
        gates_applied.append(stripped)

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
        "matrix": [[frac_cell(unitary[i][j]) for j in range(len(unitary))] for i in range(len(unitary))],
    }


def write_matrix(qasm_path: Path, out_path: Path) -> dict[str, Any]:
    data = extract_matrix(qasm_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 2:
        print("usage: qasm_matrix.py INPUT.qasm OUT.json", file=sys.stderr)
        return 2
    qasm_path = Path(args[0])
    out_path = Path(args[1])
    data = write_matrix(qasm_path, out_path)
    print(json.dumps({"ok": True, "out": str(out_path), "n_qubits": data["n_qubits"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

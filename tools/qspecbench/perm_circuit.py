"""Lightweight permutation representation for reversible OpenQASM fragments.

Does not allocate dense 2^n matrices. Supports x / cx / ccx / swap only.
"""

from __future__ import annotations

import re
from pathlib import Path

_QUBIT = re.compile(r"q\[(\d+)\]|q(\d+)", re.I)
_GATE = re.compile(
    r"^\s*(x|cx|cnot|ccx|swap)\s+(.*);?\s*$",
    re.I,
)


def _indices(args: str) -> list[int]:
    return [int(a or b) for a, b in _QUBIT.findall(args)]


def _apply_x(perm: list[int], q: int) -> None:
    bit = 1 << q
    new_perm = [0] * len(perm)
    for basis, image in enumerate(perm):
        new_perm[basis] = image ^ bit
    perm[:] = new_perm


def _apply_cx(perm: list[int], control: int, target: int) -> None:
    cbit = 1 << control
    tbit = 1 << target
    new_perm = [0] * len(perm)
    for basis, image in enumerate(perm):
        if image & cbit:
            new_perm[basis] = image ^ tbit
        else:
            new_perm[basis] = image
    perm[:] = new_perm


def _apply_ccx(perm: list[int], c0: int, c1: int, target: int) -> None:
    b0, b1, bt = 1 << c0, 1 << c1, 1 << target
    new_perm = [0] * len(perm)
    for basis, image in enumerate(perm):
        if (image & b0) and (image & b1):
            new_perm[basis] = image ^ bt
        else:
            new_perm[basis] = image
    perm[:] = new_perm


def _apply_swap(perm: list[int], a: int, b: int) -> None:
    ba, bb = 1 << a, 1 << b
    new_perm = [0] * len(perm)
    for basis, image in enumerate(perm):
        bit_a = bool(image & ba)
        bit_b = bool(image & bb)
        out = image & ~(ba | bb)
        if bit_a:
            out |= bb
        if bit_b:
            out |= ba
        new_perm[basis] = out
    perm[:] = new_perm


def apply_qasm_permutation(qasm_path: Path, n_qubits: int | None = None) -> list[int]:
    from qspecbench.resource_bounds import require_perm_circuit

    text = qasm_path.read_text(encoding="utf-8")
    if n_qubits is None:
        m = re.search(r"qubit\s*\[\s*(\d+)\s*\]", text)
        if not m:
            raise ValueError("expected qubit[n] register declaration")
        n_qubits = int(m.group(1))
    require_perm_circuit(n_qubits)
    dim = 1 << n_qubits
    # Identity as image map: basis i maps to i.
    perm = list(range(dim))
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("//") or line.lower().startswith(("openqasm", "include", "qubit")):
            continue
        match = _GATE.match(line)
        if not match:
            raise ValueError(f"permutation backend unsupported line: {line}")
        gate = match.group(1).lower()
        idxs = _indices(match.group(2))
        if gate == "x":
            _apply_x(perm, idxs[0])
        elif gate in {"cx", "cnot"}:
            _apply_cx(perm, idxs[0], idxs[1])
        elif gate == "ccx":
            _apply_ccx(perm, idxs[0], idxs[1], idxs[2])
        elif gate == "swap":
            _apply_swap(perm, idxs[0], idxs[1])
    return perm

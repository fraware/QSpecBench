"""Tests for extended OpenQASM gate matrix extraction."""

from __future__ import annotations

import math
import tempfile
from fractions import Fraction
from pathlib import Path

from qspecbench.qasm_matrix import extract_matrix


def _matrix_from_qasm(qasm: str) -> list[list[Fraction]]:
    with tempfile.NamedTemporaryFile("w", suffix=".qasm", delete=False, encoding="utf-8") as f:
        f.write(qasm)
        path = Path(f.name)
    try:
        data = extract_matrix(path)
        return [
            [Fraction(num, den) for num, den in row]
            for row in data["matrix"]
        ]
    finally:
        path.unlink(missing_ok=True)


def test_rx_pi2_matches_h():
    m_rx = _matrix_from_qasm("OPENQASM 3.0;\nqubit[1] q;\nrx(1.57079632679) q[0];\n")
    m_h = _matrix_from_qasm("OPENQASM 3.0;\nqubit[1] q;\nh q[0];\n")
    assert m_rx == m_h


def test_ccx_is_permutation():
    m = _matrix_from_qasm("OPENQASM 3.0;\nqubit[3] q;\nccx q[0], q[1], q[2];\n")
    dim = 8
    for row in m:
        assert sum(1 for x in row if x != 0) == 1
    assert len(m) == dim


def test_swap_exchanges_qubits():
    m = _matrix_from_qasm("OPENQASM 3.0;\nqubit[2] q;\nswap q[0], q[1];\n")
    col = 1
    row_one = next(i for i in range(4) if m[i][col] == Fraction(1))
    assert row_one == 2


def test_general_rx_theta():
    theta = math.pi / 4
    m = _matrix_from_qasm(f"OPENQASM 3.0;\nqubit[1] q;\nrx({theta}) q[0];\n")
    half = theta / 2.0
    c = Fraction(math.cos(half)).limit_denominator(10**12)
    s = Fraction(math.sin(half)).limit_denominator(10**12)
    assert m[0][0] == c
    assert m[0][1] == -s
    assert m[1][0] == -s
    assert m[1][1] == c

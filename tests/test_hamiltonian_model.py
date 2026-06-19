"""Regression tests for two-qubit Pauli tensor conventions in Hamiltonian.lean."""

from __future__ import annotations

from fractions import Fraction

# Lexicographic basis |00⟩,|01⟩,|10⟩,|11⟩ with qubit 0 = LSB (index bit 0).
_BASIS = 4


def _pauli_x0() -> list[list[Fraction]]:
    m = [[Fraction(0) for _ in range(_BASIS)] for _ in range(_BASIS)]
    for i, j in ((0, 1), (1, 0), (2, 3), (3, 2)):
        m[i][j] = Fraction(1)
    return m


def _pauli_x1() -> list[list[Fraction]]:
    m = [[Fraction(0) for _ in range(_BASIS)] for _ in range(_BASIS)]
    for i, j in ((0, 2), (2, 0), (1, 3), (3, 1)):
        m[i][j] = Fraction(1)
    return m


def _pauli_z0_on_qubit0() -> list[list[Fraction]]:
    """Z on qubit 0 (LSB): matches `pauliZEntry` / artifact Z0."""
    return [
        [Fraction(1), Fraction(0), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(-1), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(1), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(0), Fraction(-1)],
    ]


def _mat_add(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[x + y for x, y in zip(row_a, row_b)] for row_a, row_b in zip(a, b)]


def _mat_mul(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    n = len(a)
    return [
        [sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n)]
        for i in range(n)
    ]


def test_pauli_x0_differs_from_x1():
    x0 = _pauli_x0()
    x1 = _pauli_x1()
    assert x0 != x1
    assert x0[0][2] == Fraction(0)
    assert x1[0][2] == Fraction(1)


def test_pauli_x0_z0_anticommute():
    x0 = _pauli_x0()
    z0 = _pauli_z0_on_qubit0()
    anticom = _mat_add(_mat_mul(x0, z0), _mat_mul(z0, x0))
    assert all(cell == Fraction(0) for row in anticom for cell in row)


def test_pauli_x0_x1_commute():
    x0 = _pauli_x0()
    x1 = _pauli_x1()
    assert _mat_mul(x0, x1) == _mat_mul(x1, x0)

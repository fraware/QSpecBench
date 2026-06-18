#!/usr/bin/env python3
"""Generate and verify an independently checkable QFT scaffold certificate."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path


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


def _h() -> list[list[Fraction]]:
    return [[Fraction(1), Fraction(1)], [Fraction(1), Fraction(-1)]]


def _cnot() -> list[list[Fraction]]:
    dim = 4
    mat = _eye(dim)
    mat[2][2] = Fraction(0)
    mat[3][3] = Fraction(0)
    mat[2][3] = Fraction(1)
    mat[3][2] = Fraction(1)
    return mat


def _qft2() -> list[list[Fraction]]:
    h = _kron(_h(), _eye(2))
    cx = _cnot()
    return _mat_mul(h, _mat_mul(cx, h))


def _scale(s: int, m: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[s * x for x in row] for row in m]


def _mat_eq(a: list[list[Fraction]], b: list[list[Fraction]]) -> bool:
    return all(a[i][j] == b[i][j] for i in range(len(a)) for j in range(len(a)))


def main() -> None:
    qft = _qft2()
    product = _mat_mul(qft, qft)
    target = _scale(4, _eye(4))
    equal = _mat_eq(product, target)
    cert = {
        "certificate_type": "unitary_equality_small_instance",
        "claim_id": "qft_inverse_qft_small_instance",
        "method": "exact_matrix_multiplication",
        "n_qubits": 2,
        "relation": "QFT @ QFT = 4 I (unnormalized integer model)",
        "equal": equal,
        "generator": "evidence/verify_unitary_equality.py",
        "notes": "Matches Lean QFT2 unnormalized model; not a general OpenQASM semantics proof.",
    }
    out = Path(__file__).with_name("unitary_equality.certificate.json")
    out.write_text(json.dumps(cert, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": equal, "certificate": str(out)}))
    if not equal:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

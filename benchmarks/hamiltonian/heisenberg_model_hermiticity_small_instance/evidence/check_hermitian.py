"""Heuristic Hermiticity check for Pauli-decomposed Hamiltonians (not a proof)."""

from __future__ import annotations

import json
import re
from pathlib import Path

I = ((1, 0), (0, 1))
X = ((0, 1), (1, 0))
Y = ((0, -1j), (1j, 0))
Z = ((1, 0), (0, -1))
PAULI = {"I": I, "X": X, "Y": Y, "Z": Z}
TERM_RE = re.compile(r"([XYZI])(\d+)")


def kron(a, b):
    return tuple(
        tuple(a[i][j] * b[k][l] for j in range(2) for l in range(2))
        for i in range(2) for k in range(2)
    )


def zeros(n):
    return tuple(tuple(0j for _ in range(n)) for _ in range(n))


def mat_add(a, b):
    return tuple(tuple(a[i][j] + b[i][j] for j in range(len(a))) for i in range(len(a)))


def mat_scale(s, a):
    return tuple(tuple(s * a[i][j] for j in range(len(a))) for i in range(len(a)))


def dagger(a):
    return tuple(tuple(a[j][i].conjugate() for j in range(len(a))) for i in range(len(a)))


def mat_eq(a, b, tol=1e-9):
    return all(abs(a[i][j] - b[i][j]) < tol for i in range(len(a)) for j in range(len(a)))


def pauli_matrix(label: str, n_qubits: int):
    ops = ["I"] * n_qubits
    for axis, idx in TERM_RE.findall(label.replace(" ", "")):
        ops[int(idx)] = axis
    mat = PAULI[ops[0]]
    for op in ops[1:]:
        mat = kron(mat, PAULI[op])
    return mat


def main() -> None:
    claim_dir = Path(__file__).resolve().parents[1]
    data = json.loads((claim_dir / "artifacts/hamiltonian.json").read_text(encoding="utf-8"))
    terms = data.get("terms", [])
    if not terms:
        raise SystemExit("no terms")
    n_qubits = 1 + max(int(m.group(2)) for t in terms for m in TERM_RE.finditer(t["operators"]))
    dim = 2**n_qubits
    total = zeros(dim)
    for term in terms:
        coeff = term["coeff"]
        if not isinstance(coeff, (int, float)):
            raise SystemExit("coefficients must be real numbers")
        total = mat_add(total, mat_scale(coeff, pauli_matrix(term["operators"], n_qubits)))
    if not mat_eq(total, dagger(total)):
        raise SystemExit("Hamiltonian failed numeric Hermiticity check")
    print(json.dumps({"ok": True, "trust_level": "heuristic", "message": "Hermitian under numeric Pauli check"}))


if __name__ == "__main__":
    main()

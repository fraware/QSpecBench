#!/usr/bin/env python3
"""Generate and verify an independently checkable unitary equality certificate."""

from __future__ import annotations

import json
import sys
from pathlib import Path

I = ((1, 0), (0, 1))
X = ((0, 1), (1, 0))
Z = ((1, 0), (0, -1))
O = ((0, 0), (0, 0))


def kron(a, b):
    return tuple(
        tuple(a[i][j] * b[k][l] for j in range(2) for l in range(2))
        for i in range(2) for k in range(2)
    )


def mat_mul(a, b):
    n = len(a)
    return tuple(
        tuple(sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n))
        for i in range(n)
    )


def mat_eq(a, b):
    return all(a[i][j] == b[i][j] for i in range(len(a)) for j in range(len(a)))


def main() -> None:
    cx = (
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (0, 0, 0, 1),
        (0, 0, 1, 0),
    )
    identity = (
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (0, 0, 1, 0),
        (0, 0, 0, 1),
    )
    cx_sq = mat_mul(cx, cx)
    equal = mat_eq(cx_sq, identity)
    cert = {
        "certificate_type": "unitary_equality_small_instance",
        "claim_id": "cnot_self_inverse_cancellation",
        "method": "exact_matrix_multiplication",
        "n_qubits": 2,
        "relation": "CX @ CX = I",
        "equal": equal,
        "notes": "Independently checkable for this fixed 2-qubit instance; not a general formal proof.",
    }
    out = Path(__file__).with_name("unitary_equality.certificate.json")
    out.write_text(json.dumps(cert, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": equal, "certificate": str(out)}))
    if not equal:
        sys.exit(1)


if __name__ == "__main__":
    main()

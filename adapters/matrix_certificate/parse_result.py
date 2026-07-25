"""Independent matrix certificate checker.

Does not import qasm_matrix, denotate, or bridge_codegen. Verifies a JSON
certificate relating two declared matrices under an exact or global-phase relation.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


def _as_complex(entry: Any) -> complex:
    if isinstance(entry, complex):
        return entry
    if isinstance(entry, (int, float)):
        return complex(entry)
    if isinstance(entry, list) and len(entry) == 2:
        return complex(float(entry[0]), float(entry[1]))
    if isinstance(entry, dict) and "re" in entry and "im" in entry:
        return complex(float(entry["re"]), float(entry["im"]))
    raise ValueError(f"unsupported matrix entry: {entry!r}")


def _load_matrix(payload: Any) -> list[list[complex]]:
    if isinstance(payload, str):
        payload = json.loads(payload)
    if not isinstance(payload, list) or not payload:
        raise ValueError("matrix must be a non-empty nested list")
    rows: list[list[complex]] = []
    for row in payload:
        if not isinstance(row, list):
            raise ValueError("matrix rows must be lists")
        rows.append([_as_complex(x) for x in row])
    width = len(rows[0])
    if any(len(r) != width for r in rows):
        raise ValueError("matrix is jagged")
    if len(rows) != width:
        raise ValueError("matrix must be square")
    return rows


def _matrices_equal(a: list[list[complex]], b: list[list[complex]], *, tol: float) -> bool:
    if len(a) != len(b):
        return False
    for ra, rb in zip(a, b):
        if len(ra) != len(rb):
            return False
        for x, y in zip(ra, rb):
            if abs(x - y) > tol:
                return False
    return True


def _global_phase_equal(
    a: list[list[complex]], b: list[list[complex]], *, tol: float
) -> bool:
    """Exact up to a single global complex phase of unit modulus."""
    n = len(a)
    phase: complex | None = None
    for i in range(n):
        for j in range(n):
            x, y = a[i][j], b[i][j]
            if abs(x) <= tol and abs(y) <= tol:
                continue
            if abs(x) <= tol or abs(y) <= tol:
                return False
            cand = y / x
            if abs(abs(cand) - 1.0) > tol:
                return False
            if phase is None:
                phase = cand
            elif abs(cand - phase) > tol:
                return False
    if phase is None:
        return True
    scaled = [[phase * x for x in row] for row in a]
    return _matrices_equal(scaled, b, tol=tol)


def check_matrix_certificate(path: Path | str) -> dict[str, Any]:
    """Validate an independent matrix certificate JSON file."""
    path = Path(path)
    errors: list[str] = []
    try:
        cert = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "errors": [f"invalid certificate: {exc}"], "trust_level": "independently_checkable"}

    required = ("gate_profile", "n_qubits", "source_matrix", "target_matrix", "relation")
    for key in required:
        if key not in cert:
            errors.append(f"missing field {key!r}")
    if errors:
        return {"ok": False, "errors": errors, "trust_level": "independently_checkable"}

    n = cert["n_qubits"]
    if not isinstance(n, int) or n < 1 or n > 8:
        errors.append(f"n_qubits out of supported range: {n!r}")
    relation = cert["relation"]
    if relation not in {"exact", "global_phase"}:
        errors.append(f"unsupported relation {relation!r}")

    try:
        source = _load_matrix(cert["source_matrix"])
        target = _load_matrix(cert["target_matrix"])
    except ValueError as exc:
        errors.append(str(exc))
        return {"ok": False, "errors": errors, "trust_level": "independently_checkable"}

    expected_dim = 2 ** int(n) if isinstance(n, int) and n >= 1 else None
    if expected_dim and len(source) != expected_dim:
        errors.append(f"source_matrix dim {len(source)} != 2**n_qubits ({expected_dim})")
    if expected_dim and len(target) != expected_dim:
        errors.append(f"target_matrix dim {len(target)} != 2**n_qubits ({expected_dim})")

    tol = float(cert.get("tolerance", 1e-9))
    if not errors:
        if relation == "exact":
            if not _matrices_equal(source, target, tol=tol):
                errors.append("matrices are not exactly equal within tolerance")
        elif relation == "global_phase":
            if not _global_phase_equal(source, target, tol=tol):
                errors.append("matrices are not equal up to global phase")

    return {
        "ok": not errors,
        "errors": errors,
        "checker": "independent_matrix_certificate",
        "trust_level": "independently_checkable",
        "gate_profile": cert.get("gate_profile"),
        "relation": relation,
        "n_qubits": n,
    }


def check(path: Path) -> dict[str, Any]:
    """Adapter-style entrypoint."""
    return check_matrix_certificate(path)

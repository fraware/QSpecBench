"""Stabilizer code JSON validator for QSpecBench QEC artifacts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PAULI_RE = re.compile(r"^[IXYZ_]+$")
PAULI_TO_VEC = {"I": 0, "X": 1, "Y": 2, "Z": 3}


def _pauli_char(p: str, idx: int) -> str:
    if idx >= len(p):
        return "I"
    ch = p[idx]
    return ch if ch in "IXYZ" else "I"


def _pauli_commute(a: str, b: str) -> bool:
    n = max(len(a), len(b))
    anticommute = 0
    for i in range(n):
        pa = _pauli_char(a, i)
        pb = _pauli_char(b, i)
        if pa == "I" or pb == "I" or pa == pb:
            continue
        anticommute += 1
    return anticommute % 2 == 0


def validate_code(data: dict) -> tuple[list[str], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    checks_run: list[str] = ["schema_structure"]

    if data.get("type") != "stabilizer_code":
        errors.append("type must be stabilizer_code")
    params = data.get("parameters", {})
    for key in ("n", "k", "d"):
        if key not in params:
            errors.append(f"parameters.{key} required")
    stabilizers = data.get("stabilizers", [])
    if not stabilizers:
        errors.append("at least one stabilizer required")
    for s in stabilizers:
        pauli = s.get("pauli", "")
        if not PAULI_RE.match(pauli):
            errors.append(f"invalid pauli string: {pauli}")
    logicals = data.get("logical_operators", [])
    for op in logicals:
        pauli = op.get("pauli", "")
        if not PAULI_RE.match(pauli):
            errors.append(f"invalid logical pauli: {pauli}")
    n = params.get("n")
    if isinstance(n, int):
        for s in stabilizers:
            if len(s.get("pauli", "")) != n:
                errors.append(f"stabilizer length must be n={n}")
        for op in logicals:
            if len(op.get("pauli", "")) != n:
                errors.append(f"logical operator length must be n={n}")

    if len(stabilizers) >= 2 and not errors:
        checks_run.append("stabilizer_commutation")
        labels = [s.get("label", s.get("pauli", "?")) for s in stabilizers]
        paulis = [s.get("pauli", "") for s in stabilizers]
        for i in range(len(paulis)):
            for j in range(i + 1, len(paulis)):
                if not _pauli_commute(paulis[i], paulis[j]):
                    errors.append(
                        f"stabilizers {labels[i]} and {labels[j]} anticommute"
                    )

    if logicals and stabilizers and not errors:
        checks_run.append("logical_stabilizer_commutation")
        for op in logicals:
            op_label = op.get("label", op.get("pauli", "?"))
            op_pauli = op.get("pauli", "")
            for s in stabilizers:
                s_label = s.get("label", s.get("pauli", "?"))
                if not _pauli_commute(op_pauli, s.get("pauli", "")):
                    errors.append(
                        f"logical {op_label} anticommutes with stabilizer {s_label}"
                    )

    if isinstance(params.get("d"), int) and isinstance(n, int) and isinstance(params.get("k"), int):
        checks_run.append("distance_consistency")
        d = params["d"]
        k = params["k"]
        if d < 1:
            warnings.append("distance d < 1")
        if n and k and d > n - k + 1:
            warnings.append("distance d exceeds Singleton bound for declared n,k")
        if len(stabilizers) < n - k:
            warnings.append("fewer stabilizers than n-k; code may be under-specified")

    return errors, warnings, checks_run


def check(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    errors, warnings, checks_run = validate_code(data)
    return {
        "ok": not errors,
        "adapter": "qec_json_validator",
        "path": str(path),
        "trust_level": "tool_checked",
        "checks_run": checks_run,
        "warnings": warnings,
        "errors": errors,
    }


def main() -> None:
    path = Path(sys.argv[1])
    result = check(path)
    out = path.with_suffix(".validated.json")
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()

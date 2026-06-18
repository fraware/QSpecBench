"""Stabilizer code JSON validator for QSpecBench QEC artifacts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PAULI_RE = re.compile(r"^[IXYZ_]+$")


def validate_code(data: dict) -> list[str]:
    errors: list[str] = []
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
    return errors


def check(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_code(data)
    return {
        "ok": not errors,
        "adapter": "qec_json_validator",
        "path": str(path),
        "trust_level": "tool_checked",
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

"""QCEC wrapper stub: validates artifact presence and documents manual equivalence check."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def check(source: Path, target: Path | None = None) -> dict:
    errors: list[str] = []
    if not source.is_file():
        errors.append(f"missing source: {source}")
    if target and not target.is_file():
        errors.append(f"missing target: {target}")
    return {
        "ok": not errors,
        "adapter": "qcec_wrapper",
        "path": str(source),
        "target": str(target) if target else None,
        "trust_level": "externally_trusted",
        "manual_step": "Run QCEC externally; this adapter only verifies artifacts exist.",
        "errors": errors,
    }


def main() -> None:
    source = Path(sys.argv[1])
    target = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    result = check(source, target)
    print(json.dumps(result))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()

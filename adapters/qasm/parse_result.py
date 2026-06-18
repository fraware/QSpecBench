"""QASM syntax validation (structure only, not semantic equivalence)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED_PATTERNS = [
    re.compile(r"OPENQASM\s+[\d.]+", re.IGNORECASE),
    re.compile(r"\bqubit\b", re.IGNORECASE),
]
FORBIDDEN_EMPTY = re.compile(r"^\s*$", re.MULTILINE)


def check(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if FORBIDDEN_EMPTY.match(text) or not text.strip():
        errors.append("empty file")
    for pattern in REQUIRED_PATTERNS:
        if not pattern.search(text):
            errors.append(f"missing pattern: {pattern.pattern}")
    if "measure" in text.lower() and "bit" not in text.lower():
        errors.append("measurement without classical bit declaration")
    ok = not errors
    return {
        "ok": ok,
        "adapter": "qasm_parse",
        "path": str(path),
        "trust_level": "syntax_only",
        "errors": errors,
    }


def main() -> None:
    path = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else path.with_suffix(path.suffix + ".parse.json")
    result = check(path)
    out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()

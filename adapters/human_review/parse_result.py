"""Validate human-review markdown artifacts contain substantive review content."""

from __future__ import annotations

import json
import sys
from pathlib import Path

MIN_CHARS = 80
KEYWORDS = ("proof", "claim", "theorem", "assume", "unitary", "state", "qubit", "formal")


def check(path: Path) -> dict:
    errors: list[str] = []
    if not path.is_file():
        errors.append(f"missing review file: {path}")
        return {
            "ok": False,
            "adapter": "human_review",
            "path": str(path),
            "trust_level": "externally_trusted",
            "errors": errors,
        }

    text = path.read_text(encoding="utf-8").strip()
    if len(text) < MIN_CHARS:
        errors.append(f"review too short ({len(text)} chars; need >= {MIN_CHARS})")
    lower = text.lower()
    if not any(k in lower for k in KEYWORDS):
        errors.append("review missing expected domain keywords")

    return {
        "ok": not errors,
        "adapter": "human_review",
        "path": str(path),
        "trust_level": "externally_trusted",
        "errors": errors,
    }


def main() -> None:
    path = Path(sys.argv[1])
    result = check(path)
    print(json.dumps(result))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()

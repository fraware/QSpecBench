"""Validate AI formalization rubric files contain required fields."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SCORE_RE = re.compile(r"score\s*:\s*([0-5])", re.IGNORECASE)


def check(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if "rubric" not in text.lower() and "semantic" not in text.lower():
        errors.append("missing rubric heading")
    if not SCORE_RE.search(text):
        errors.append("missing score field (0-5)")
    return {
        "ok": not errors,
        "adapter": "ai_formalization_rubric",
        "path": str(path),
        "trust_level": "untrusted",
        "errors": errors,
        "score": int(SCORE_RE.search(text).group(1)) if SCORE_RE.search(text) else None,
    }


def main() -> None:
    path = Path(sys.argv[1])
    result = check(path)
    print(json.dumps(result))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()

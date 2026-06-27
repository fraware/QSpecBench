"""Isabelle proof evidence stub — kernel not configured in CI."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def check(evidence_file: Path) -> dict:
    return {
        "ok": False,
        "adapter": "isabelle_proof",
        "path": str(evidence_file),
        "trust_level": "not_checked",
        "skipped": True,
        "errors": ["Isabelle kernel not configured in CI; adapter reserved for future use"],
    }


def main() -> None:
    path = Path(sys.argv[1]).resolve()
    result = check(path)
    print(json.dumps(result))
    sys.exit(0 if result.get("ok") else 1)


if __name__ == "__main__":
    main()

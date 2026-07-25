"""Validate human-review markdown artifacts contain substantive review content.

The adapter is a **heuristic** length/keyword check only. It must not be treated
as sufficient to satisfy ``required_for_claim`` for ``artifact_bound_reference_claim``
(ABRC) or ``reference_claim`` promotions — dual hash-bound review JSON
(``status.reviews`` + ``review_artifact.schema.json``) is the authority (F-026).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

MIN_CHARS = 80
KEYWORDS = ("proof", "claim", "theorem", "assume", "unitary", "state", "qubit", "formal")

# Explicit: heuristic pass must not gate ABRC/RC required_for_claim (trust.py).
CANNOT_SATISFY_REQUIRED_FOR_CLAIM_MATURITIES = frozenset(
    {"artifact_bound_reference_claim", "reference_claim"}
)


def check(path: Path) -> dict:
    errors: list[str] = []
    if not path.is_file():
        errors.append(f"missing review file: {path}")
        return {
            "ok": False,
            "adapter": "human_review",
            "path": str(path),
            "trust_level": "externally_trusted",
            "satisfies_required_for_claim": False,
            "notes": (
                "heuristic length/keyword check only; ABRC/RC required_for_claim "
                "requires dual hash-bound review JSON"
            ),
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
        # F-026: never claim this adapter alone satisfies ABRC/RC required_for_claim.
        "satisfies_required_for_claim": False,
        "cannot_satisfy_required_for_claim_maturities": sorted(
            CANNOT_SATISFY_REQUIRED_FOR_CLAIM_MATURITIES
        ),
        "notes": (
            "heuristic length/keyword check only; ABRC/RC promotions require "
            "dual hash-bound review JSON (reviews.py), not this adapter alone"
        ),
        "errors": errors,
    }


def main() -> None:
    path = Path(sys.argv[1])
    result = check(path)
    print(json.dumps(result))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()

"""Heuristic BK mapping sanity check (not a proof)."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    claim_dir = Path(__file__).resolve().parents[1]
    data = json.loads((claim_dir / "artifacts/hamiltonian.json").read_text(encoding="utf-8"))
    terms = data.get("terms", [])
    if len(terms) < 2:
        raise SystemExit("need at least two terms for mapping scaffold check")
    mapping = data.get("mapping", "")
    if mapping != "bravyi_kitaev":
        raise SystemExit("expected bravyi_kitaev mapping")
    print(json.dumps({"ok": True, "trust_level": "heuristic", "message": "BK mapping declared with multi-term Hamiltonian"}))


if __name__ == "__main__":
    main()

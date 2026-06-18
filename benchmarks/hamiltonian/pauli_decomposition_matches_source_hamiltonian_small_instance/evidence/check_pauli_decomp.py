"""Heuristic Pauli decomposition consistency check (not a proof)."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    claim_dir = Path(__file__).resolve().parents[1]
    data = json.loads((claim_dir / "artifacts/hamiltonian.json").read_text(encoding="utf-8"))
    terms = data.get("terms", [])
    if not terms:
        raise SystemExit("no terms")
    for term in terms:
        if "coeff" not in term or "operators" not in term:
            raise SystemExit("malformed term")
    print(json.dumps({"ok": True, "trust_level": "heuristic", "message": "Pauli terms present with coefficients"}))


if __name__ == "__main__":
    main()

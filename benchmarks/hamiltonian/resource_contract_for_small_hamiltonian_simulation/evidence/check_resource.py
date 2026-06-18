"""Heuristic resource contract check (not a proof)."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    claim_dir = Path(__file__).resolve().parents[1]
    spec_path = claim_dir / "spec.yaml"
    text = spec_path.read_text(encoding="utf-8")
    if "resources:" not in text or "enabled: true" not in text:
        raise SystemExit("resource contract not enabled in spec")
    data = json.loads((claim_dir / "artifacts/hamiltonian.json").read_text(encoding="utf-8"))
    if not data.get("terms"):
        raise SystemExit("hamiltonian terms required")
    print(json.dumps({"ok": True, "trust_level": "heuristic", "message": "Resource contract and Hamiltonian artifact present"}))


if __name__ == "__main__":
    main()

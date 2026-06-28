"""Validate JSON dynamic-simulation evidence (freshness + all_ok)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def check(evidence_path: Path) -> dict:
    errors: list[str] = []
    if not evidence_path.is_file():
        return {
            "ok": False,
            "adapter": "dynamic_simulation",
            "errors": ["evidence file missing"],
        }

    try:
        payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "adapter": "dynamic_simulation",
            "path": str(evidence_path),
            "errors": [f"invalid JSON: {exc}"],
        }

    claim_dir = evidence_path.parent.parent
    from qspecbench.dynamic_simulation_evidence import validate_dynamic_simulation_evidence
    from qspecbench.validate import load_spec

    spec = load_spec(claim_dir / "spec.yaml")
    errors.extend(validate_dynamic_simulation_evidence(claim_dir, spec))

    if payload.get("type") == "teleportation_basis_check_v0":
        if not payload.get("all_ok"):
            errors.append("teleportation_basis_check_v0 requires all_ok=true")
    elif payload.get("all_ok") is False:
        errors.append("simulation report all_ok is false")

    return {
        "ok": not errors,
        "adapter": "dynamic_simulation",
        "path": str(evidence_path),
        "trust_level": "heuristic",
        "errors": errors,
    }


def main() -> None:
    path = Path(sys.argv[1]).resolve()
    result = check(path)
    print(json.dumps(result))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()

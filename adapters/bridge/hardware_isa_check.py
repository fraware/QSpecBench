"""Hardware ISA abstraction adapter wrapper.

Adapts ``qspecbench.hardware_isa_adapter.verify_hardware_isa_abstraction`` (which
takes an explicit ``--profile``/``--out`` pair) to the single-positional-argument
``{path}`` calling convention used by ``evidence_runner`` for evidence entries whose
``checker`` is ``hardware_isa_adapter``. The profile artifact is resolved by
convention at ``artifacts/hardware_isa_profile.json`` under the claim directory.
Never claims ``hardware_semantics`` / ``device_fidelity`` / ``pulse_schedule_semantics``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def check(evidence_path: Path) -> dict:
    claim_dir = evidence_path.parent.parent
    from qspecbench.hardware_isa_adapter import (
        HardwareIsaAdapterError,
        verify_hardware_isa_abstraction,
    )

    profile_path = claim_dir / "artifacts" / "hardware_isa_profile.json"
    errors: list[str] = []
    if not profile_path.is_file():
        result: dict = {"ok": False}
        errors = [f"hardware ISA profile missing: {profile_path}"]
    else:
        try:
            result = verify_hardware_isa_abstraction(profile_path)
        except HardwareIsaAdapterError as exc:
            result = {"ok": False}
            errors = [str(exc)]

    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return {
        "ok": result.get("ok", False),
        "adapter": "hardware_isa_abstraction",
        "path": str(evidence_path),
        "trust_level": "checked",
        "checker": "hardware_isa_adapter",
        "errors": errors,
    }


def main() -> None:
    path = Path(sys.argv[1]).resolve()
    result = check(path)
    print(json.dumps(result))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()

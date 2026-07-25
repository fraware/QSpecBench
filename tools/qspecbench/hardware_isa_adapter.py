# -*- coding: utf-8 -*-
"""Fail-closed hardware ISA abstraction adapter (not device fidelity).

Records backend/ISA identifiers and content hashes for an offline or simulated
hardware profile. Never treats simulation success as ``hardware_semantics`` /
device fidelity. Checked obligation target: ``hardware_abstraction_isa_layer``.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ADAPTER_SCHEMA = "qspecbench.hardware_isa_abstraction.v1"
ISA_LAYER_ID = "openqasm3_canonical_ast_software_isa_v1"


class HardwareIsaAdapterError(ValueError):
    pass


def sha256_payload(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_hardware_isa_abstraction(
    profile_path: Path,
    *,
    require_offline: bool = True,
) -> dict[str, Any]:
    """Validate an ISA/hardware-profile JSON without claiming device execution."""
    if not profile_path.is_file():
        raise HardwareIsaAdapterError(f"hardware ISA profile missing: {profile_path}")
    data = json.loads(profile_path.read_text(encoding="utf-8"))
    if data.get("schema") != "qspecbench.hardware_isa_profile.v1":
        raise HardwareIsaAdapterError(f"unexpected profile schema {data.get('schema')!r}")
    backend_id = data.get("backend_id")
    isa_id = data.get("isa_id")
    mode = data.get("execution_mode")
    if not isinstance(backend_id, str) or not backend_id:
        raise HardwareIsaAdapterError("backend_id required")
    if not isinstance(isa_id, str) or not isa_id:
        raise HardwareIsaAdapterError("isa_id required")
    if mode not in ("offline_simulated", "offline_recorded", "abstract_isa_only"):
        raise HardwareIsaAdapterError(
            f"execution_mode {mode!r} not allowed for ISA abstraction "
            "(device_live forbidden)"
        )
    if require_offline and mode == "device_live":
        raise HardwareIsaAdapterError("device_live execution is fail-closed here")
    if data.get("claims_device_fidelity") is True:
        raise HardwareIsaAdapterError(
            "profile must not claim device fidelity under ISA abstraction"
        )
    if data.get("hardware_semantics_checked") is True:
        raise HardwareIsaAdapterError(
            "profile must not set hardware_semantics_checked=true "
            "(use hardware_abstraction_isa_layer instead)"
        )
    if data.get("pulse_schedule_semantics_checked") is True:
        raise HardwareIsaAdapterError(
            "profile must not set pulse_schedule_semantics_checked=true "
            "(ISA abstraction cannot discharge pulse_schedule_semantics)"
        )
    if data.get("claims_pulse_schedule_semantics") is True:
        raise HardwareIsaAdapterError(
            "profile must not claim pulse_schedule_semantics under ISA abstraction"
        )
    # Reject profiles that list device/pulse obligations as satisfied.
    for key in ("satisfied_obligations", "supports"):
        raw = data.get(key)
        if not isinstance(raw, list):
            continue
        banned = {
            "hardware_semantics",
            "device_fidelity",
            "pulse_schedule_semantics",
        } & {str(x) for x in raw}
        if banned:
            raise HardwareIsaAdapterError(
                f"profile {key} must not include device/pulse residuals: "
                + ", ".join(sorted(banned))
            )

    result: dict[str, Any] = {
        "schema": ADAPTER_SCHEMA,
        "ok": True,
        "isa_layer_id": ISA_LAYER_ID,
        "backend_id": backend_id,
        "isa_id": isa_id,
        "execution_mode": mode,
        "profile_sha256": sha256_file(profile_path),
        "claims_device_fidelity": False,
        "claims_pulse_schedule_semantics": False,
        "hardware_semantics_checked": False,
        "pulse_schedule_semantics_checked": False,
        "hardware_abstraction_isa_layer": True,
        "satisfied_obligations": ["hardware_abstraction_isa_layer"],
        "command": f"python -m qspecbench.hardware_isa_adapter --profile {profile_path.name}",
        "notes": (
            "Fail-closed ISA/hardware-profile abstraction. Records backend/ISA IDs + "
            "hashes for offline/simulated profiles only. Does NOT check device "
            "fidelity, pulse schedules, or live hardware execution "
            "(hardware_semantics / device_fidelity / pulse_schedule_semantics "
            "remain not_checked)."
        ),
    }
    result["output_sha256"] = sha256_payload(
        {k: v for k, v in result.items() if k != "output_sha256"}
    )
    return result


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = verify_hardware_isa_abstraction(args.profile)
    except HardwareIsaAdapterError as exc:
        payload = {
            "schema": ADAPTER_SCHEMA,
            "ok": False,
            "hardware_semantics_checked": False,
            "pulse_schedule_semantics_checked": False,
            "hardware_abstraction_isa_layer": False,
            "claims_device_fidelity": False,
            "claims_pulse_schedule_semantics": False,
            "satisfied_obligations": [],
            "error": str(exc),
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(exc, file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": result["ok"], "output_sha256": result["output_sha256"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

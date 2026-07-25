# -*- coding: utf-8 -*-
"""Declared-universe Stim spacetime MWPM verifiers.

Two independent declared, finite universes (explicit, bounded — never unbounded
all-codes MWPM):

1. Repetition-code memory: Stim ``Circ.generated('repetition_code:memory', ...)``
   for every odd distance ``d ∈ {3, 5, 7}`` with ``rounds = d`` and
   ``after_clifford_depolarization = 0.01`` (``verify_declared_repetition_universe``).
2. Rotated surface-code memory: Stim
   ``Circ.generated('surface_code:rotated_memory_z', ...)`` for distance
   ``d = 3`` with ``rounds = 3`` and ``after_clifford_depolarization = 0.01``
   (``verify_declared_surface_universe``). This is a singleton declared universe
   (``d ≤ 3``, currently only ``d = 3``); it is a *different* declared universe
   from the repetition-code one above and is never renamed to it.

Both require per-member DEM + declared decode table certificates already agreed
by ``stim_pymatching_adapter``. Each verifier only checks that every universe
member has a passing certificate with ``full_spacetime_mwpm`` still false at the
unbounded level — the checked label is the declared-universe discharge.

``unbounded_all_codes_mwpm`` is permanently not applicable (open-ended code family)
for both universes; neither this module nor any caller may set it to checked.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from qspecbench.stim_pymatching_adapter import (
    StimPyMatchingAdapterError,
    verify_stim_pymatching_dem,
)

# Explicit declared universe (odd d ≤ 7, R = d).
DECLARED_UNIVERSE: list[dict[str, Any]] = [
    {
        "distance": 3,
        "rounds": 3,
        "after_clifford_depolarization": 0.01,
        "dem": "bitflip_spacetime_d3_R3.dem",
        "table": "declared_decode_table_bitflip_spacetime_d3_R3.json",
        "label": "spacetime_mwpm_3qubit_bitflip_R3",
        "expected_detectors": 8,
    },
    {
        "distance": 5,
        "rounds": 5,
        "after_clifford_depolarization": 0.01,
        "dem": "bitflip_spacetime_d5_R5.dem",
        "table": "declared_decode_table_bitflip_spacetime_d5_R5.json",
        "label": "spacetime_mwpm_repetition_d5_R5",
        "expected_detectors": 24,
    },
    {
        "distance": 7,
        "rounds": 7,
        "after_clifford_depolarization": 0.01,
        "dem": "bitflip_spacetime_d7_R7.dem",
        "table": "declared_decode_table_bitflip_spacetime_d7_R7.json",
        "label": "spacetime_mwpm_repetition_d7_R7",
        "expected_detectors": 48,
    },
]

UNIVERSE_ID = "stim_repetition_memory_odd_d_le_7_R_eq_d_p0p01"

# Explicit declared surface-code universe (currently the singleton d=3 member;
# "d <= 3" reads as "d in {3}" until additional members are added). This is a
# distinct declared universe from the repetition-code one above.
DECLARED_SURFACE_UNIVERSE: list[dict[str, Any]] = [
    {
        "distance": 3,
        "rounds": 3,
        "after_clifford_depolarization": 0.01,
        "circuit_kind": "surface_code:rotated_memory_z",
        "dem": "surface_spacetime_d3_R3.dem",
        "table": "declared_decode_table_surface_spacetime_d3_R3.json",
        "label": "spacetime_mwpm_surface_d3_R3",
        "expected_detectors": 24,
    },
]

SURFACE_UNIVERSE_ID = "stim_surface_rotated_memory_d_eq_3_R_eq_3_p0p01"


class DeclaredUniverseError(ValueError):
    pass


def sha256_payload(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def verify_declared_repetition_universe(artifacts_dir: Path) -> dict[str, Any]:
    """Verify every member of the declared Stim repetition spacetime universe."""
    members: list[dict[str, Any]] = []
    for spec in DECLARED_UNIVERSE:
        dem = artifacts_dir / spec["dem"]
        table = artifacts_dir / spec["table"]
        if not dem.is_file() or not table.is_file():
            raise DeclaredUniverseError(
                f"missing universe member artifacts for d={spec['distance']}: "
                f"{dem.name}, {table.name}"
            )
        try:
            member = verify_stim_pymatching_dem(dem, table)
        except StimPyMatchingAdapterError as exc:
            raise DeclaredUniverseError(
                f"universe member d={spec['distance']} failed: {exc}"
            ) from exc
        if member.get("dem_num_detectors") != spec["expected_detectors"]:
            raise DeclaredUniverseError(
                f"d={spec['distance']}: detectors "
                f"{member.get('dem_num_detectors')} != {spec['expected_detectors']}"
            )
        if member.get("full_spacetime_mwpm") is True:
            raise DeclaredUniverseError(
                "member must not claim unbounded full_spacetime_mwpm=true"
            )
        members.append(
            {
                "distance": spec["distance"],
                "rounds": spec["rounds"],
                "label": spec["label"],
                "ok": member["ok"],
                "dem_num_detectors": member["dem_num_detectors"],
                "dem_sha256": member["dem_sha256"],
                "table_sha256": member["table_sha256"],
                "output_sha256": member["output_sha256"],
                "agreed_faults": member["agreed_faults"],
            }
        )

    ok = all(m["ok"] for m in members) and len(members) == len(DECLARED_UNIVERSE)
    result: dict[str, Any] = {
        "schema": "qspecbench.stim_declared_repetition_universe.v1",
        "ok": ok,
        "universe_id": UNIVERSE_ID,
        "universe_description": (
            "Stim Circ.generated repetition_code:memory for all odd d in {3,5,7} "
            "with rounds=d and after_clifford_depolarization=0.01; PyMatching "
            "Blossom agreement on declared generating-set tables per member."
        ),
        "unbounded_all_codes_mwpm": False,
        "unbounded_all_codes_mwpm_status": "not_applicable",
        "unbounded_all_codes_mwpm_note": (
            "Open-ended code/distance/round family; only finite declared universes "
            "admit certificates."
        ),
        "full_spacetime_mwpm": True,  # true ONLY under declared universe discharge
        "full_spacetime_mwpm_scope": UNIVERSE_ID,
        "members": members,
        "notes": (
            "Declared-universe discharge of full_spacetime_mwpm for "
            f"{UNIVERSE_ID}. Not unbounded all-codes / all-distances MWPM "
            "(permanently not_applicable)."
        ),
    }
    # Fail-closed honesty: never emit a renamed/unbounded universe payload.
    from qspecbench.permanent_residuals import validate_stim_declared_universe_payload

    honesty = validate_stim_declared_universe_payload(result)
    if honesty:
        raise DeclaredUniverseError("; ".join(honesty))
    result["output_sha256"] = sha256_payload(
        {k: v for k, v in result.items() if k != "output_sha256"}
    )
    if not ok:
        raise DeclaredUniverseError("declared universe verification failed")
    return result


def verify_declared_surface_universe(artifacts_dir: Path) -> dict[str, Any]:
    """Verify every member of the declared Stim rotated-surface-code universe.

    Distinct from ``verify_declared_repetition_universe``: different
    ``universe_id``, different Stim generated-circuit family
    (``surface_code:rotated_memory_z``), and currently a singleton member set
    (``d = 3``). Never renamed to the repetition universe or to unbounded
    all-codes MWPM.
    """
    members: list[dict[str, Any]] = []
    for spec in DECLARED_SURFACE_UNIVERSE:
        dem = artifacts_dir / spec["dem"]
        table = artifacts_dir / spec["table"]
        if not dem.is_file() or not table.is_file():
            raise DeclaredUniverseError(
                f"missing surface universe member artifacts for d={spec['distance']}: "
                f"{dem.name}, {table.name}"
            )
        try:
            member = verify_stim_pymatching_dem(dem, table)
        except StimPyMatchingAdapterError as exc:
            raise DeclaredUniverseError(
                f"surface universe member d={spec['distance']} failed: {exc}"
            ) from exc
        if member.get("dem_num_detectors") != spec["expected_detectors"]:
            raise DeclaredUniverseError(
                f"d={spec['distance']}: detectors "
                f"{member.get('dem_num_detectors')} != {spec['expected_detectors']}"
            )
        if member.get("full_spacetime_mwpm") is True:
            raise DeclaredUniverseError(
                "surface universe member must not claim unbounded full_spacetime_mwpm=true"
            )
        members.append(
            {
                "distance": spec["distance"],
                "rounds": spec["rounds"],
                "circuit_kind": spec["circuit_kind"],
                "label": spec["label"],
                "ok": member["ok"],
                "dem_num_detectors": member["dem_num_detectors"],
                "dem_sha256": member["dem_sha256"],
                "table_sha256": member["table_sha256"],
                "output_sha256": member["output_sha256"],
                "agreed_faults": member["agreed_faults"],
            }
        )

    ok = all(m["ok"] for m in members) and len(members) == len(DECLARED_SURFACE_UNIVERSE)
    result: dict[str, Any] = {
        "schema": "qspecbench.stim_declared_surface_universe.v1",
        "ok": ok,
        "universe_id": SURFACE_UNIVERSE_ID,
        "universe_description": (
            "Stim Circ.generated surface_code:rotated_memory_z for d=3 (singleton "
            "declared universe; d<=3) with rounds=3 and "
            "after_clifford_depolarization=0.01; PyMatching Blossom agreement on "
            "declared generating-set tables per member."
        ),
        "unbounded_all_codes_mwpm": False,
        "unbounded_all_codes_mwpm_status": "not_applicable",
        "unbounded_all_codes_mwpm_note": (
            "Open-ended code/distance/round family; only finite declared universes "
            "admit certificates. Distinct from the repetition-code declared universe."
        ),
        "full_spacetime_mwpm_surface": True,  # true ONLY under declared universe discharge
        "full_spacetime_mwpm_surface_scope": SURFACE_UNIVERSE_ID,
        "members": members,
        "notes": (
            "Declared-universe discharge of full_spacetime_mwpm_surface for "
            f"{SURFACE_UNIVERSE_ID}. Not unbounded all-codes / all-distances MWPM "
            "(permanently not_applicable); not the repetition-code declared "
            f"universe ({UNIVERSE_ID})."
        ),
    }
    from qspecbench.permanent_residuals import validate_stim_declared_universe_payload

    honesty = validate_stim_declared_universe_payload(result)
    if honesty:
        raise DeclaredUniverseError("; ".join(honesty))
    result["output_sha256"] = sha256_payload(
        {k: v for k, v in result.items() if k != "output_sha256"}
    )
    if not ok:
        raise DeclaredUniverseError("declared surface universe verification failed")
    return result


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--universe",
        choices=("repetition", "surface"),
        default="repetition",
        help="Which declared universe to verify (default: repetition).",
    )
    args = parser.parse_args(argv)
    if args.universe == "surface":
        verify_fn = verify_declared_surface_universe
        error_schema = "qspecbench.stim_declared_surface_universe.v1"
        error_universe_id = SURFACE_UNIVERSE_ID
        error_flag_key = "full_spacetime_mwpm_surface"
    else:
        verify_fn = verify_declared_repetition_universe
        error_schema = "qspecbench.stim_declared_repetition_universe.v1"
        error_universe_id = UNIVERSE_ID
        error_flag_key = "full_spacetime_mwpm"
    try:
        result = verify_fn(args.artifacts)
    except (DeclaredUniverseError, StimPyMatchingAdapterError) as exc:
        payload = {
            "schema": error_schema,
            "ok": False,
            "universe_id": error_universe_id,
            error_flag_key: False,
            "unbounded_all_codes_mwpm": False,
            "unbounded_all_codes_mwpm_status": "not_applicable",
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

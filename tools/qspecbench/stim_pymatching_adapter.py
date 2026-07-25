# -*- coding: utf-8 -*-
"""Stim-invoked DEM → PyMatching Blossom agreement adapter.

Invokes real Stim to parse a DetectorErrorModel, builds PyMatching Matching via
`from_detector_error_model`, and compares finite fixture cases to a declared table.
Never treats a bare success string as a certificate. Honest label: Stim-invoked DEM
fragment — not full spacetime MWPM.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

STIM_PIN = "1.16.0"
PYMATCHING_PIN = "2.4.0"


class StimPyMatchingAdapterError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_payload(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _require_stim():
    try:
        import stim
    except ImportError as exc:
        raise StimPyMatchingAdapterError(
            f"stim not installed; pin stim=={STIM_PIN} (optional extra qec-matching)"
        ) from exc
    ver = getattr(stim, "__version__", "unknown")
    if ver != STIM_PIN:
        raise StimPyMatchingAdapterError(
            f"stim version {ver!r} != pinned {STIM_PIN!r}"
        )
    return stim


def _require_pymatching():
    try:
        import pymatching
    except ImportError as exc:
        raise StimPyMatchingAdapterError(
            f"pymatching not installed; pin pymatching=={PYMATCHING_PIN}"
        ) from exc
    ver = getattr(pymatching, "__version__", "unknown")
    if ver != PYMATCHING_PIN:
        raise StimPyMatchingAdapterError(
            f"pymatching version {ver!r} != pinned {PYMATCHING_PIN!r}"
        )
    return pymatching


def load_table(table_path: Path) -> dict[str, Any]:
    if not table_path.is_file():
        raise StimPyMatchingAdapterError(f"declared decode table missing: {table_path}")
    data = json.loads(table_path.read_text(encoding="utf-8"))
    if data.get("schema") != "qspecbench.declared_decode_table.v1":
        raise StimPyMatchingAdapterError(f"unexpected table schema {data.get('schema')!r}")
    if not data.get("cases"):
        raise StimPyMatchingAdapterError("declared decode table requires cases")
    return data


def build_matching_from_dem(dem_path: Path):
    stim = _require_stim()
    pymatching = _require_pymatching()
    if not dem_path.is_file():
        raise StimPyMatchingAdapterError(f"DEM missing: {dem_path}")
    dem_text = dem_path.read_text(encoding="utf-8")
    dem = stim.DetectorErrorModel(dem_text)
    matching = pymatching.Matching.from_detector_error_model(dem)
    return stim, pymatching, dem, matching, dem_text


def decode_syndrome(matching, syndrome_bits: list[int]) -> list[int]:
    import numpy as np

    syn = np.array(syndrome_bits, dtype=np.uint8)
    # Stim DEM detectors only — truncate/pad to num_detectors
    n = matching.num_detectors
    if len(syn) < n:
        syn = np.pad(syn, (0, n - len(syn)))
    elif len(syn) > n:
        syn = syn[:n]
    pred = matching.decode(syn)
    return [int(x) for x in pred]


def verify_stim_pymatching_dem(
    dem_path: Path,
    table_path: Path,
) -> dict[str, Any]:
    """Compare Stim→PyMatching decode to declared fixture table on finite cases."""
    stim, pymatching, dem, matching, dem_text = build_matching_from_dem(dem_path)
    table = load_table(table_path)
    agreed: list[str] = []
    disagreed: list[str] = []
    outside_ok: list[str] = []
    outside_fail: list[str] = []
    case_details: list[dict[str, Any]] = []

    for case in table["cases"]:
        name = str(case["name"])
        syndrome = list(case["syndrome_bits"])
        # Table expected_prediction is fixture-graph shaped (may include boundary).
        # For Stim DEM we compare detector-length predictions against a Stim-specific
        # expected field when present; else compare truncated fixture prediction.
        # Table expected_prediction is fault-id shaped (includes boundary L*).
        # DEM must declare matching observables so decode() returns that shape.
        expected = list(
            case.get("stim_expected_prediction") or case["expected_prediction"]
        )
        kind = case.get("kind", "in_model")
        pred = decode_syndrome(matching, syndrome)
        if len(pred) < len(expected):
            pred = pred + [0] * (len(expected) - len(pred))
        elif len(pred) > len(expected):
            pred = pred[: len(expected)]
        detail = {
            "name": name,
            "kind": kind,
            "syndrome_bits": syndrome[: matching.num_detectors],
            "expected_prediction": expected,
            "stim_pymatching_prediction": pred,
            "agree": pred == expected,
        }
        case_details.append(detail)
        if kind == "outside":
            if pred == expected:
                outside_ok.append(name)
            else:
                outside_fail.append(name)
                disagreed.append(name)
        else:
            if pred == expected:
                agreed.append(name)
            else:
                disagreed.append(name)

    ok = not disagreed and not outside_fail and len(agreed) > 0
    command = (
        "python -m qspecbench.stim_pymatching_adapter "
        f"--dem {dem_path.name} --table {table_path.name}"
    )
    result: dict[str, Any] = {
        "schema": "qspecbench.stim_pymatching_dem.v1",
        "ok": ok,
        "stim_invoked": True,
        "pymatching_invoked": True,
        "full_spacetime_mwpm": False,
        "stim_version": stim.__version__,
        "pymatching_version": pymatching.__version__,
        "command": command,
        "dem_sha256": hashlib.sha256(dem_text.encode("utf-8")).hexdigest(),
        "dem_num_detectors": int(dem.num_detectors),
        "table_sha256": sha256_file(table_path),
        "agreed_faults": agreed,
        "disagreed_faults": disagreed,
        "outside_checked": outside_ok,
        "outside_failed": outside_fail,
        "case_details": case_details,
        "notes": (
            "Stim-invoked DetectorErrorModel + PyMatching Blossom on declared 2x7 "
            "time-chain fragment. Not full spacetime MWPM; not Lean kernel of Stim."
        ),
    }
    result["output_sha256"] = sha256_payload(
        {k: v for k, v in result.items() if k != "output_sha256"}
    )
    if not ok:
        raise StimPyMatchingAdapterError(
            "Stim/PyMatching DEM agreement failed: "
            + ", ".join(disagreed or outside_fail or ["unknown"])
        )
    return result


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dem", type=Path, required=True)
    parser.add_argument("--table", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = verify_stim_pymatching_dem(args.dem, args.table)
    except StimPyMatchingAdapterError as exc:
        payload = {
            "schema": "qspecbench.stim_pymatching_dem.v1",
            "ok": False,
            "stim_invoked": False,
            "pymatching_invoked": False,
            "full_spacetime_mwpm": False,
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

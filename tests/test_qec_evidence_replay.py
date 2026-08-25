"""Fail-closed regressions for QEC result replay and artifact binding."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from adapters.qec.stim_matching_check import check

REPO = Path(__file__).resolve().parents[1]
CLAIM = REPO / "benchmarks/qec/three_qubit_bit_flip_code_corrects_one_x"
ARTIFACT = CLAIM / "artifacts/stim_compatible_dem_2x7.json"
RESULT = CLAIM / "evidence/stim_dem_adapter_result.json"


def test_recorded_dem_result_binds_current_claim_artifact_by_exact_hash() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["path"] == "artifacts/stim_compatible_dem_2x7.json"
    actual = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()
    assert payload["sha256"] == actual


def test_recorded_dem_result_replays_fail_closed_and_passes() -> None:
    result = check(RESULT)
    assert result["ok"] is True
    assert result["checker"] == "stim_dem_adapter"
    assert result["errors"] == []

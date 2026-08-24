"""Fail-closed replay tests for typed Stim/PyMatching evidence dispatch."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from adapters.qec.stim_matching_check import (
    StimMatchingCheckError,
    _resolve_recorded_artifact,
    check,
)

REPO = Path(__file__).resolve().parents[1]
BITFLIP = REPO / "benchmarks/qec/three_qubit_bit_flip_code_corrects_one_x"
SURFACE = REPO / "benchmarks/qec/surface_code_distance_three_stabilizer_sanity"


def test_historical_windows_path_replays_by_recorded_sha256() -> None:
    evidence = BITFLIP / "evidence/stim_dem_adapter_result.json"
    result = check(evidence)
    assert result["ok"] is True
    assert result["checker"] == "stim_dem_adapter"


def test_surface_declared_universe_is_bound_to_stim_matching_adapter() -> None:
    sidecar = json.loads((SURFACE / "evidence_adapters.json").read_text(encoding="utf-8"))
    assert sidecar["bindings"]["stim_declared_surface_universe"] == (
        "qspecbench.qec.stim_matching.v1"
    )


def test_hash_fallback_requires_unique_claim_artifact(tmp_path: Path) -> None:
    claim = tmp_path / "claim"
    artifacts = claim / "artifacts"
    artifacts.mkdir(parents=True)
    payload = b"same bytes"
    digest = hashlib.sha256(payload).hexdigest()
    (artifacts / "a.json").write_bytes(payload)
    (artifacts / "b.json").write_bytes(payload)

    historical = {
        "path": r"C:\\old-machine\\artifact.json",
        "sha256": digest,
    }
    with pytest.raises(StimMatchingCheckError, match="ambiguously"):
        _resolve_recorded_artifact(historical, claim)


def test_relative_recorded_path_must_match_recorded_hash(tmp_path: Path) -> None:
    claim = tmp_path / "claim"
    artifacts = claim / "artifacts"
    artifacts.mkdir(parents=True)
    artifact = artifacts / "dem.json"
    artifact.write_bytes(b"actual")
    historical = {
        "path": "artifacts/dem.json",
        "sha256": hashlib.sha256(b"different").hexdigest(),
    }
    with pytest.raises(StimMatchingCheckError, match="SHA-256 mismatch"):
        _resolve_recorded_artifact(historical, claim)

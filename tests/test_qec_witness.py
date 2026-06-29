"""Tests for QEC witness hash export helper."""

from __future__ import annotations

import json
from pathlib import Path

from qspecbench.qec_external import validate_qec_external_certificate
from qspecbench.qec_witness import (
    export_small_code_witness,
    syndrome_table_sha256,
    verify_witness_table_hashes,
)

REPO = Path(__file__).resolve().parents[1]
BIT_FLIP = REPO / "benchmarks/qec/three_qubit_bit_flip_code_corrects_one_x"


def test_syndrome_table_sha256_stable():
    table_path = BIT_FLIP / "artifacts/syndrome_table.json"
    table = json.loads(table_path.read_text(encoding="utf-8"))
    h1 = syndrome_table_sha256(table)
    h2 = syndrome_table_sha256(table)
    assert h1 == h2
    assert len(h1) == 64


def test_export_small_code_witness_includes_syndrome_hash():
    witness = export_small_code_witness(
        syndrome_table_path=BIT_FLIP / "artifacts/syndrome_table.json",
        correction_table_path=BIT_FLIP / "artifacts/correction_table.json",
        complete_for="[[3,1,3]] bit-flip lookup decoder",
    )
    assert witness["method"] == "lookup_table"
    assert witness["syndrome_table_sha256"]
    assert witness["correction_table_sha256"]
    assert witness["complete_for"]


def test_verify_witness_table_hashes_positive():
    witness = export_small_code_witness(
        syndrome_table_path=BIT_FLIP / "artifacts/syndrome_table.json",
        correction_table_path=BIT_FLIP / "artifacts/correction_table.json",
        complete_for="[[3,1,3]] bit-flip lookup decoder",
    )
    assert verify_witness_table_hashes(witness, BIT_FLIP) == []


def test_validate_witness_fields_requires_complete_for():
    from qspecbench.qec_witness import validate_witness_fields

    errors = validate_witness_fields({"method": "lookup_table"})
    assert any("complete_for" in e for e in errors)


def test_qec_external_rejects_witness_missing_complete_for():
    cert = {
        "certificate_version": "qec-external-v0-stub",
        "claim_kind": "logical_preservation",
        "code_ref": {"artifact_sha256": "a" * 64},
        "prover": {"name": "stub", "method": "schema_only"},
        "result": {
            "status": "unknown",
            "witness": {"method": "lookup_table", "syndrome_table_sha256": "b" * 64},
        },
    }
    errors = validate_qec_external_certificate(cert, BIT_FLIP, {"id": "three_qubit_bit_flip_code_corrects_one_x"})
    assert any("complete_for" in e for e in errors)


def test_backfilled_qec_witness_json_matches_export():
    stored = json.loads((BIT_FLIP / "expected/qec_witness.json").read_text(encoding="utf-8"))
    assert stored.get("complete_for")
    assert verify_witness_table_hashes(stored, BIT_FLIP) == []


def test_verify_witness_table_hashes_negative():
    witness = export_small_code_witness(
        syndrome_table_path=BIT_FLIP / "artifacts/syndrome_table.json",
        correction_table_path=BIT_FLIP / "artifacts/correction_table.json",
        complete_for="[[3,1,3]] bit-flip lookup decoder",
    )
    witness["syndrome_table_sha256"] = "0" * 64
    errors = verify_witness_table_hashes(witness, BIT_FLIP)
    assert any("syndrome_table_sha256 mismatch" in e for e in errors)


def test_qec_external_rejects_claim_kind_method_mismatch():
    witness = export_small_code_witness(
        syndrome_table_path=BIT_FLIP / "artifacts/syndrome_table.json",
        correction_table_path=BIT_FLIP / "artifacts/correction_table.json",
        complete_for="[[3,1,3]] bit-flip lookup decoder",
    )
    cert = {
        "certificate_version": "qec-external-v0-stub",
        "claim_kind": "minimum_distance",
        "code_ref": {"artifact_sha256": "a" * 64},
        "prover": {"name": "stub", "method": "schema_only"},
        "result": {"status": "unknown", "witness": witness},
    }
    errors = validate_qec_external_certificate(cert, BIT_FLIP, {"id": "three_qubit_bit_flip_code_corrects_one_x"})
    assert any("incompatible with claim_kind" in e for e in errors)


def test_validate_qec_witness_deep_on_expected_file():
    from qspecbench.qec_witness import validate_qec_witness

    stored = json.loads((BIT_FLIP / "expected/qec_witness.json").read_text(encoding="utf-8"))
    assert validate_qec_witness(stored, BIT_FLIP) == []


def test_qec_external_certificate_validates_witness_hashes():
    witness = export_small_code_witness(
        syndrome_table_path=BIT_FLIP / "artifacts/syndrome_table.json",
        correction_table_path=BIT_FLIP / "artifacts/correction_table.json",
        complete_for="[[3,1,3]] bit-flip lookup decoder",
    )
    cert = {
        "certificate_version": "qec-external-v0-stub",
        "claim_kind": "logical_preservation",
        "code_ref": {
            "benchmark_id": "three_qubit_bit_flip_code_corrects_one_x",
            "artifact_path": "artifacts/code.json",
            "artifact_sha256": "0" * 64,
        },
        "prover": {"name": "stub", "method": "schema_only"},
        "result": {"status": "unknown", "witness": witness},
    }
    errors = validate_qec_external_certificate(cert, BIT_FLIP, {"id": "three_qubit_bit_flip_code_corrects_one_x"})
    assert not any("syndrome_table_sha256 mismatch" in e for e in errors)

"""Tests for QEC witness hash export helper."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from qspecbench.qec_external import validate_qec_external_certificate
from qspecbench.qec_witness import (
    export_small_code_witness,
    syndrome_table_sha256,
    validate_qec_witness,
    verify_witness_table_hashes,
)
from qspecbench.validate import _infer_qec_witness_claim_kind, load_spec

REPO = Path(__file__).resolve().parents[1]
BIT_FLIP = REPO / "benchmarks/qec/three_qubit_bit_flip_code_corrects_one_x"
QEC_ROOT = REPO / "benchmarks/qec"
DISTANCE_CERT = REPO / "benchmarks/qec/distance_certificate_small_css_code"


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


def test_all_qec_benchmarks_have_certificate_level():
    specs = sorted(QEC_ROOT.glob("*/spec.yaml"))
    assert len(specs) == 13
    missing: list[str] = []
    levels: dict[str, int] = {}
    for spec_path in specs:
        spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        level = (spec.get("qec_claim_scope") or {}).get("qec_certificate_level")
        if not level:
            missing.append(spec_path.parent.name)
        else:
            levels[level] = levels.get(level, 0) + 1
    assert not missing, f"missing qec_certificate_level: {missing}"
    assert levels.get("qec_small_code_checked") == 12
    assert levels.get("qec_external_certificate_checked") == 1


def test_all_stored_qec_witness_files_validate_with_claim_kind():
    for witness_path in sorted(QEC_ROOT.glob("*/expected/qec_witness.json")):
        claim_dir = witness_path.parent.parent
        spec = load_spec(claim_dir / "spec.yaml")
        witness = json.loads(witness_path.read_text(encoding="utf-8"))
        claim_kind = _infer_qec_witness_claim_kind(spec)
        assert validate_qec_witness(witness, claim_dir, claim_kind=claim_kind) == []


def test_infer_qec_witness_claim_kind_syndrome_extraction():
    spec = load_spec(QEC_ROOT / "surface_code_single_round_syndrome_extraction/spec.yaml")
    assert _infer_qec_witness_claim_kind(spec) == "syndrome_extraction"


def test_validate_qec_witness_rejects_method_claim_kind_mismatch():
    witness = export_small_code_witness(
        syndrome_table_path=BIT_FLIP / "artifacts/syndrome_table.json",
        correction_table_path=BIT_FLIP / "artifacts/correction_table.json",
        complete_for="test scope",
    )
    errors = validate_qec_witness(witness, BIT_FLIP, claim_kind="minimum_distance")
    assert any("incompatible with claim_kind" in e for e in errors)


def test_distance_external_certificate_witness_and_verifier_hash():
    spec = load_spec(DISTANCE_CERT / "spec.yaml")
    cert = json.loads((DISTANCE_CERT / "expected/qec_external_certificate.json").read_text(encoding="utf-8"))
    errors = validate_qec_external_certificate(cert, DISTANCE_CERT, spec)
    assert errors == [], errors
    witness = cert["result"]["witness"]
    assert witness["method"] == "bruteforce_weight_enumeration"
    assert witness.get("verifier_result_sha256")
    assert witness.get("complete_for")


def test_all_qec_witnesses_have_complete_for():
    from qspecbench.qec_witness import validate_qec_witness

    qec_root = REPO / "benchmarks" / "qec"
    for witness_path in qec_root.glob("*/expected/qec_witness.json"):
        witness = json.loads(witness_path.read_text(encoding="utf-8"))
        assert witness.get("complete_for"), f"missing complete_for in {witness_path}"
        errors = validate_qec_witness(witness, witness_path.parent.parent)
        assert not any("complete_for" in e for e in errors), witness_path


def test_qec_track_classification_counts():
    """E1: 12 small-code checked + 1 external certificate benchmark."""
    small = 0
    external = 0
    for spec_path in (REPO / "benchmarks" / "qec").glob("*/spec.yaml"):
        spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        level = (spec.get("qec_claim_scope") or {}).get("qec_certificate_level")
        if level == "qec_external_certificate_checked":
            external += 1
        elif level == "qec_small_code_checked":
            small += 1
    assert external == 1
    assert small == 12

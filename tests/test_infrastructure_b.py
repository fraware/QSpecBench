"""Tests for artifact JSON schema validation and promotion smoke checks."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

import yaml

from qspecbench.artifact_schemas import validate_claim_artifacts
from qspecbench.evidence_runner import run_evidence_checks
from qspecbench.provenance import validate_provenance
from qspecbench.validate import validate_path

REPO = Path(__file__).resolve().parents[1]
MINIMAL = REPO / "schema" / "examples" / "minimal.spec.yaml"


def _minimal_spec_text(**overrides: object) -> str:
    spec = yaml.safe_load(MINIMAL.read_text(encoding="utf-8"))
    spec.update(overrides)
    return yaml.dump(spec, sort_keys=False)


def test_qec_code_json_validates_against_schema():
    claim = REPO / "benchmarks/qec/three_qubit_bit_flip_code_corrects_one_x"
    spec = yaml.safe_load((claim / "spec.yaml").read_text(encoding="utf-8"))
    errors = validate_claim_artifacts(spec, claim)
    assert not errors, errors


def test_provenance_drift_detected():
    claim = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation"
    results = validate_path(claim)
    assert results and results[0].ok


def test_raw_command_blocked_without_env():
    with tempfile.TemporaryDirectory() as tmp:
        claim = Path(tmp)
        (claim / "spec.yaml").write_text(
            _minimal_spec_text(
                id="raw_cmd_test",
                track="algorithm",
                domain="test",
                claim_type="test_claim",
                evidence=[
                    {
                        "id": "raw_evidence",
                        "type": "human_review",
                        "path": "README.md",
                        "checker": "manual",
                        "command": "echo hello",
                        "status": "passing",
                    }
                ],
                claim_scope={
                    "headline_claim_id": "raw_cmd_test_headline",
                    "headline_claim_text": "Raw command block test",
                    "required_obligations": ["test"],
                },
                proved_scope={"checked_obligations": [], "unproved_obligations": ["test"]},
                headline_claim_status={"status": "unproved", "notes": None},
            ),
            encoding="utf-8",
        )
        (claim / "README.md").write_text("# test\n", encoding="utf-8")
        env_before = os.environ.pop("QSPECBENCH_ALLOW_RAW_COMMANDS", None)
        try:
            results = run_evidence_checks(claim)
            raw = [r for r in results if r.evidence_id == "raw_evidence"]
            assert raw and not raw[0].ok
            assert any("raw command" in e.lower() for e in raw[0].errors)
        finally:
            if env_before is not None:
                os.environ["QSPECBENCH_ALLOW_RAW_COMMANDS"] = env_before


def test_provenance_drift_fails_validation():
    claim = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation"
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / "claim"
        shutil.copytree(claim, copy)
        spec = yaml.safe_load((copy / "spec.yaml").read_text(encoding="utf-8"))
        artifact = copy / "artifacts/source.qasm"
        artifact.write_bytes(artifact.read_bytes() + b"\n")
        errors = validate_provenance(spec, copy)
        assert any("sha256 drift" in e for e in errors)


def test_logical_preservation_bit_flip_code():
    from adapters.qec.parse_result import check

    path = REPO / "benchmarks/qec/three_qubit_bit_flip_code_corrects_one_x/artifacts/code.json"
    result = check(path)
    assert result["ok"], result.get("errors")
    checks = result.get("check_results", {})
    assert checks.get("logical_preservation") is True
    assert checks.get("syndrome") is True
    assert checks.get("correction") is True
    assert "single_pauli_error_correction_validator" in result.get("checks_run", [])


def test_qec_z_error_labels_phase_flip():
    from adapters.qec.parse_result import check

    path = REPO / "benchmarks/qec/three_qubit_phase_flip_code_corrects_one_z/artifacts/code.json"
    result = check(path)
    assert result["ok"], result.get("errors")
    assert result["check_results"].get("syndrome") is True


def test_qec_verifier_result_evidence_resolves_code_json():
    from adapters.qec.parse_result import _resolve_check_target

    evidence = REPO / "benchmarks/qec/three_qubit_bit_flip_code_corrects_one_x/evidence/qec_verifier_result.json"
    code = _resolve_check_target(evidence)
    assert code.name == "code.json"
    assert code.is_file()


def test_full_dynamic_semantics_rejected_at_validate():
    with tempfile.TemporaryDirectory() as tmp:
        claim = Path(tmp)
        (claim / "spec.yaml").write_text(
            _minimal_spec_text(
                id="dynamic_mode_test",
                track="algorithm",
                domain="test",
                claim_type="test_claim",
                qasm_extraction={"mode": "full_dynamic_semantics", "allowed_to_skip": []},
                semantics_base="openqasm_fragment",
                claim_scope={
                    "headline_claim_id": "dynamic_mode_test_headline",
                    "headline_claim_text": "Dynamic mode fail-closed test",
                    "required_obligations": ["test"],
                },
                proved_scope={"checked_obligations": [], "unproved_obligations": ["test"]},
                headline_claim_status={"status": "unproved", "notes": None},
            ),
            encoding="utf-8",
        )
        results = validate_path(claim)
        assert results and not results[0].ok
        assert any("full_dynamic_semantics" in e for e in results[0].errors)

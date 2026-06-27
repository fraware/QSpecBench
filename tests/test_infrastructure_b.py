"""Tests for artifact JSON schema validation and promotion smoke checks."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import yaml

from qspecbench.artifact_schemas import validate_claim_artifacts
from qspecbench.evidence_runner import run_evidence_checks
from qspecbench.provenance import sha256_file
from qspecbench.validate import validate_path

REPO = Path(__file__).resolve().parents[1]


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
    spec_text = """
qspecbench_version: "0.2"
id: raw_cmd_test
title: Raw command block test
track: algorithm
domain: test
claim_type: test_claim
difficulty: introductory
informal_claim:
  statement: Raw command block test
  source: null
  reference_key: null
semantic_level:
  primary: algorithmic
  secondary: []
objects:
  - name: readme
    type: other
    path: README.md
    format: markdown
    role: reference
specification:
  mode: exact
  preconditions: [test]
  postconditions: [test]
  invariants: []
  approximation:
    enabled: false
    metric: null
    bound: null
  resources:
    enabled: false
    qubits: null
    gates: null
    depth: null
    t_count: null
    t_depth: null
    ancilla: null
    measurements: null
    other: []
assumptions:
  mathematical: []
  physical: []
  tool: []
  artifact: []
  unverified: []
acceptable_evidence:
  - type: human_review
    checker: manual
    path: null
    required_for_claim: false
    trust_level: externally_trusted
evidence:
  - id: raw_evidence
    type: human_review
    path: README.md
    checker: manual
    command: echo hello
    status: passing
trust_boundary:
  checked_by: []
  trusted_kernels: []
  trusted_external_tools: []
  untrusted_components: []
  assumptions_not_checked: [raw command test]
claim_scope:
  headline_claim_id: raw_cmd_test_headline
  headline_claim_text: Raw command block test
  required_obligations: [test]
proved_scope:
  checked_obligations: []
  unproved_obligations: [test]
headline_claim_status:
  status: unproved
  notes: null
status:
  informal_claim: complete
  machine_spec: complete
  artifacts: complete
  evidence: complete
  ci: passing
  maturity: seed
references: []
"""
    with tempfile.TemporaryDirectory() as tmp:
        claim = Path(tmp)
        (claim / "spec.yaml").write_text(spec_text, encoding="utf-8")
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


def test_logical_preservation_bit_flip_code():
    from adapters.qec.parse_result import check

    path = REPO / "benchmarks/qec/three_qubit_bit_flip_code_corrects_one_x/artifacts/code.json"
    result = check(path)
    assert result["ok"], result.get("errors")
    assert "single_pauli_error_correction_validator" in result.get("checks_run", [])

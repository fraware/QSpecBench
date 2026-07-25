"""Fixture tests for QBricks and ZX adapters (Wave 0.2)."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import yaml

from qspecbench.adapter_registry import (
    EVIDENCE_TYPE_ADAPTERS,
    REGISTERED_ADAPTERS,
    adapter_for_evidence_type,
    validate_adapter_name,
    validate_evidence_adapter_binding,
)
from qspecbench.adapter_types import AdapterRequest
from qspecbench.schema import load_schema

REPO = Path(__file__).resolve().parents[1]
ZX_EXAMPLES = REPO / "adapters" / "zx" / "examples"
QBRICKS_EXAMPLES = REPO / "adapters" / "qbricks" / "examples"
FAKE_QBRICKS = QBRICKS_EXAMPLES / "fake_qbricks_cli.py"


def test_qbricks_zx_registered_in_registry():
    assert "qbricks" in REGISTERED_ADAPTERS
    assert "zx" in REGISTERED_ADAPTERS
    assert validate_adapter_name("qbricks") == []
    assert validate_adapter_name("zx") == []
    assert adapter_for_evidence_type("qbricks_result") == "qbricks"
    assert adapter_for_evidence_type("zx_certificate") == "zx"
    assert EVIDENCE_TYPE_ADAPTERS["qbricks_result"] == "qbricks"
    assert EVIDENCE_TYPE_ADAPTERS["zx_certificate"] == "zx"


def test_qbricks_zx_in_primary_schema():
    schema = load_schema()
    enum = schema["$defs"]["evidence_type"]["enum"]
    assert "qbricks_result" in enum
    assert "zx_certificate" in enum

    spec = yaml.safe_load(
        (REPO / "schema" / "examples" / "minimal.spec.yaml").read_text(encoding="utf-8")
    )
    spec["evidence"] = [
        {
            "id": "zx_ev",
            "type": "zx_certificate",
            "path": "evidence/zx.json",
            "checker": "qspecbench.zx_independent.v1",
            "status": "not_checked",
        },
        {
            "id": "qb_ev",
            "type": "qbricks_result",
            "path": "evidence/qb.json",
            "checker": "qbricks",
            "status": "not_checked",
        },
    ]
    jsonschema.validate(spec, schema)


def test_zx_happy_path_fixture_certificate():
    from adapters.zx.parse_result import check

    result = check(ZX_EXAMPLES / "valid_normal_form.json")
    assert result.ok
    assert not result.skipped
    assert result.adapter == "zx"
    assert result.tool_version
    assert result.command
    assert result.input_hashes.get("certificate")
    assert result.output_hash
    assert len(result.output_hash) == 64
    assert result.trust_level == "independently_checkable"


def test_zx_forged_success_certificate_fails():
    from adapters.zx.parse_result import check

    result = check(ZX_EXAMPLES / "forged_success.json")
    assert not result.ok
    assert result.errors
    assert any("forged" in e or "schema_version" in e for e in result.errors)
    assert result.input_hashes.get("certificate")
    # Still records hashes even on failure (no silent bare pass).
    assert result.ok is False


def test_zx_mismatched_normal_forms_fail(tmp_path):
    from adapters.zx.parse_result import check

    cert = {
        "schema_version": "qspecbench.zx_certificate.v1",
        "relation": "normal_form_equality",
        "n_qubits": 1,
        "source_normal_form": {
            "generators": [{"kind": "Z", "phase_pi_rational": [0, 1], "arity": 2}]
        },
        "target_normal_form": {
            "generators": [{"kind": "X", "phase_pi_rational": [0, 1], "arity": 2}]
        },
    }
    path = tmp_path / "mismatch.json"
    path.write_text(json.dumps(cert), encoding="utf-8")
    result = check(AdapterRequest(path=path, evidence_type="zx_certificate"))
    assert not result.ok
    assert any("not equal" in e for e in result.errors)


def test_qbricks_missing_tool_fail_closed(monkeypatch):
    from adapters.qbricks import parse_result

    monkeypatch.delenv("QSPECBENCH_QBRICKS_BIN", raising=False)
    monkeypatch.setattr(parse_result, "_resolve_qbricks_bin", lambda: None)
    result = parse_result.check(QBRICKS_EXAMPLES / "valid_result.json")
    assert not result.ok
    assert result.skipped
    assert result.trust_level == "unsupported"
    assert any("missing" in e.lower() for e in result.errors)
    assert result.input_hashes


def test_qbricks_forged_certificate_fails(monkeypatch):
    from adapters.qbricks import parse_result

    # Even with a tool present, forged bare-success JSON is rejected before invoke.
    monkeypatch.setenv("QSPECBENCH_QBRICKS_BIN", str(FAKE_QBRICKS))
    result = parse_result.check(QBRICKS_EXAMPLES / "forged_success.json")
    assert not result.ok
    assert not result.skipped
    assert any("forged" in e or "schema_version" in e for e in result.errors)


def test_qbricks_happy_path_with_fixture_cli(monkeypatch):
    from adapters.qbricks import parse_result

    monkeypatch.setenv("QSPECBENCH_QBRICKS_BIN", str(FAKE_QBRICKS))

    result = parse_result.check(QBRICKS_EXAMPLES / "valid_result.json")
    assert result.ok, result.errors
    assert not result.skipped
    assert result.tool_version
    assert result.command
    assert "verify" in (result.command or "")
    assert result.input_hashes.get("circuit") or result.input_hashes.get("evidence")
    assert result.output_hash
    assert len(result.output_hash) == 64
    assert result.trust_level == "externally_trusted"
    # Python fixture CLIs are launched under the current interpreter.
    assert str(FAKE_QBRICKS) in (result.command or "")


def test_qbricks_zx_binding_allows_passing_when_registered():
    spec = {
        "evidence": [
            {
                "id": "zx",
                "type": "zx_certificate",
                "path": "evidence/x.json",
                "checker": "qspecbench.zx_independent.v1",
                "status": "passing",
            },
            {
                "id": "qb",
                "type": "qbricks_result",
                "path": "evidence/q.json",
                "checker": "qbricks",
                "status": "passing",
            },
        ],
        "acceptable_evidence": [
            {
                "type": "zx_certificate",
                "checker": "qspecbench.zx_independent.v1",
                "required_for_claim": False,
                "trust_level": "independently_checkable",
                "path": None,
            }
        ],
    }
    assert validate_evidence_adapter_binding(spec) == []


def test_unknown_evidence_type_still_fail_closed():
    spec = {
        "evidence": [
            {
                "id": "bogus",
                "type": "not_a_real_evidence_type",
                "path": "evidence/x.json",
                "checker": "none",
                "status": "passing",
            }
        ]
    }
    errors = validate_evidence_adapter_binding(spec)
    assert any("no registered adapter" in e for e in errors)

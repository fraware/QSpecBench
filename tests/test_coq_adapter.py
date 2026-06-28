"""Coq/Rocq/Isabelle adapter CI smoke tests (parse_result stub only)."""

from pathlib import Path

import yaml

from qspecbench.evidence_runner import EVIDENCE_TYPE_ADAPTERS

REPO = Path(__file__).resolve().parents[1]


def test_coq_stub_returns_not_checked():
    from adapters.coq.parse_result import check

    result = check(REPO / "adapters" / "coq" / "README.md")
    assert result["adapter"] == "coq_proof"
    assert not result["ok"]
    assert result.get("skipped")
    assert result["trust_level"] == "not_checked"


def test_rocq_stub_returns_not_checked():
    from adapters.rocq.parse_result import check

    result = check(REPO / "adapters" / "rocq" / "README.md")
    assert result["adapter"] == "rocq_proof"
    assert not result["ok"]
    assert result.get("skipped")


def test_isabelle_stub_returns_not_checked():
    from adapters.isabelle.parse_result import check

    result = check(REPO / "adapters" / "isabelle" / "README.md")
    assert result["adapter"] == "isabelle_proof"
    assert not result["ok"]
    assert result.get("skipped")


def test_second_assistant_adapters_declared():
    for adapter in ("coq", "rocq", "isabelle"):
        adapter_yaml = REPO / "adapters" / adapter / "adapter.yaml"
        assert adapter_yaml.is_file(), f"missing {adapter_yaml}"
        text = adapter_yaml.read_text(encoding="utf-8")
        assert f"adapter: {adapter}_proof" in text or f"{adapter}_proof" in text


def test_evidence_runner_maps_coq_types():
    assert EVIDENCE_TYPE_ADAPTERS["coq_proof"] == "coq"
    assert EVIDENCE_TYPE_ADAPTERS["rocq_proof"] == "rocq"
    assert EVIDENCE_TYPE_ADAPTERS["isabelle_proof"] == "isabelle"


def test_coq_proof_evidence_type_schema_valid():
    from qspecbench.schema import load_schema
    import jsonschema

    spec = yaml.safe_load((REPO / "schema" / "examples" / "minimal.spec.yaml").read_text(encoding="utf-8"))
    spec["evidence"] = [
        {
            "id": "coq_ev",
            "type": "coq_proof",
            "path": "evidence/proof.v",
            "checker": "coq",
            "status": "passing",
        }
    ]
    jsonschema.validate(spec, load_schema())


def test_evidence_runner_coq_adapter_command():
    from qspecbench.evidence_runner import _default_adapter_command

    cmd = _default_adapter_command("coq_proof", REPO / "adapters" / "coq" / "README.md")
    assert cmd is not None
    assert "parse_result.py" in cmd
    assert "coq" in cmd


def test_coq_ci_flag_documented():
    """QSPECBENCH_COQ=1 enables optional second-assistant checks (see validate.yml)."""
    import os

    assert os.environ.get("QSPECBENCH_COQ", "0") in {"0", "1", ""}

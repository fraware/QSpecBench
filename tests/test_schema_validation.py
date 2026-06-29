"""Schema validation tests."""

from pathlib import Path

import jsonschema
import pytest
import yaml

from qspecbench.schema import load_schema, validate_spec_schema
from qspecbench.validate import validate_spec_dict

REPO = Path(__file__).resolve().parents[1]
EXAMPLES = REPO / "schema" / "examples"


@pytest.fixture
def schema():
    return load_schema()


@pytest.mark.parametrize("name", [
    "minimal.spec.yaml",
    "algorithm.spec.yaml",
    "equivalence.spec.yaml",
    "qec.spec.yaml",
    "hamiltonian.spec.yaml",
    "ai_formalization.spec.yaml",
])
def test_example_specs_validate(schema, name):
    spec = yaml.safe_load((EXAMPLES / name).read_text(encoding="utf-8"))
    validate_spec_schema(spec)


def test_invalid_id_rejected(schema):
    spec = yaml.safe_load((EXAMPLES / "minimal.spec.yaml").read_text(encoding="utf-8"))
    spec["id"] = "Bad-ID"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(spec, schema)


def test_coq_proof_type_accepted(schema):
    spec = yaml.safe_load((EXAMPLES / "minimal.spec.yaml").read_text(encoding="utf-8"))
    spec["acceptable_evidence"].append({
        "type": "coq_proof",
        "checker": "coq",
        "path": None,
        "required_for_claim": False,
        "trust_level": "checked",
    })
    validate_spec_schema(spec)


def test_inline_semantic_bridge_with_codegen_hashes_validates():
    spec = yaml.safe_load((EXAMPLES / "minimal.spec.yaml").read_text(encoding="utf-8"))
    spec["semantic_bridge"] = {
        "artifact_gate_model": "openqasm3_1q2q_clifford",
        "lean_module": "QSpecBench.Quantum.OpenQASM3",
        "lean_theorem": "bridge_cnot_self_inverse",
        "normalization": {"cnot": "standard_01_control_target"},
        "claimed_link": "kernel_checked_codegen_trace",
        "wire_order": {
            "model": "openqasm_little_endian_wire_order",
            "checked_against": "lean",
        },
        "package_lean_sha256": "a" * 64,
        "theorem_identifier_sha256": "b" * 64,
        "theorem_content_sha256": "c" * 64,
    }
    validate_spec_schema(spec)


def test_inline_semantic_bridge_missing_wire_order_rejected():
    spec = yaml.safe_load((EXAMPLES / "minimal.spec.yaml").read_text(encoding="utf-8"))
    spec["semantic_bridge"] = {
        "artifact_gate_model": "openqasm3_1q2q_clifford",
        "lean_module": "QSpecBench.Quantum.OpenQASM3",
        "lean_theorem": "bridge_cnot_self_inverse",
        "normalization": {"cnot": "standard_01_control_target"},
        "claimed_link": "documented_not_proved",
    }
    with pytest.raises(jsonschema.ValidationError):
        validate_spec_schema(spec)


def test_coq_stub_adapter_fails_honestly():
    from adapters.coq.parse_result import check
    import tempfile
    from pathlib import Path

    with tempfile.NamedTemporaryFile(suffix=".v", delete=False) as f:
        path = Path(f.name)
    try:
        result = check(path)
        assert not result["ok"]
        assert result.get("skipped")
        assert result.get("trust_level") == "not_checked"
    finally:
        path.unlink(missing_ok=True)


def test_approximate_requires_bounds():
    spec = yaml.safe_load((EXAMPLES / "minimal.spec.yaml").read_text(encoding="utf-8"))
    spec["specification"]["mode"] = "approximate"
    spec["specification"]["approximation"] = {"enabled": False, "metric": None, "bound": None}
    claim_dir = REPO / "benchmarks" / "algorithms" / "no_cloning_negative_claim"
    errors, _warnings = validate_spec_dict(spec, claim_dir, REPO / "benchmarks")
    assert any("approximate" in e for e in errors)

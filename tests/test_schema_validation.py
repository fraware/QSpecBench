"""Schema validation tests."""

from pathlib import Path

import jsonschema
import pytest
import yaml

from qspecbench.schema import load_schema
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
    jsonschema.validate(spec, schema)


def test_invalid_id_rejected(schema):
    spec = yaml.safe_load((EXAMPLES / "minimal.spec.yaml").read_text(encoding="utf-8"))
    spec["id"] = "Bad-ID"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(spec, schema)


def test_coq_proof_type_rejected(schema):
    spec = yaml.safe_load((EXAMPLES / "minimal.spec.yaml").read_text(encoding="utf-8"))
    spec["acceptable_evidence"].append({
        "type": "coq_proof",
        "checker": "coq",
        "path": None,
        "required_for_claim": False,
        "trust_level": "checked",
    })
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(spec, schema)


def test_approximate_requires_bounds():
    spec = yaml.safe_load((EXAMPLES / "minimal.spec.yaml").read_text(encoding="utf-8"))
    spec["specification"]["mode"] = "approximate"
    spec["specification"]["approximation"] = {"enabled": False, "metric": None, "bound": None}
    claim_dir = REPO / "benchmarks" / "algorithms" / "no_cloning_negative_claim"
    errors = validate_spec_dict(spec, claim_dir, REPO / "benchmarks")
    assert any("approximate" in e for e in errors)

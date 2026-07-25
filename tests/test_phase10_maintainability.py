"""Phase 10 maintainability smoke tests."""

from __future__ import annotations

from pathlib import Path

from qspecbench.adapter_types import AdapterRequest, AdapterResult, result_from_legacy_dict

REPO = Path(__file__).resolve().parents[1]


def test_validation_package_modules_exist():
    root = REPO / "tools/qspecbench/validation"
    for name in (
        "schema",
        "layout",
        "claims",
        "evidence",
        "bridges",
        "qec",
        "reviews",
        "provenance",
        "result",
    ):
        assert (root / f"{name}.py").is_file(), name


def test_adapter_request_result_shape():
    req = AdapterRequest(path=Path("a.qasm"), path2=Path("b.qasm"), evidence_type="qcec_result")
    assert req.path.name == "a.qasm"
    result = AdapterResult(
        ok=True,
        errors=[],
        trust_level="externally_trusted",
        checker="qcec",
        adapter="qcec",
        input_hashes={"source": "abc"},
        output_hash="def",
        notes="ok",
    )
    payload = result.to_dict()
    assert payload["ok"] is True
    assert payload["trust_level"] == "externally_trusted"
    assert payload["input_hashes"]["source"] == "abc"

    legacy = result_from_legacy_dict(
        {"ok": False, "errors": ["x"], "adapter": "lean", "trust_level": "checked"},
        adapter="lean",
    )
    assert legacy.ok is False
    assert legacy.errors == ["x"]
    assert legacy.adapter == "lean"


def test_validate_facade_still_imports():
    from qspecbench.validate import ValidationResult, load_spec, validate_path, validate_spec_dict

    assert callable(load_spec)
    assert callable(validate_path)
    assert callable(validate_spec_dict)
    assert ValidationResult

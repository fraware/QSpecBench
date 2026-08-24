from pathlib import Path

from qspecbench.adapter_protocol import validate_adapter_request, validate_adapter_result


def _request() -> dict:
    return {
        "schema": "qspecbench.adapter_request.v1",
        "adapter_id": "qspecbench.test.v1",
        "adapter_version": "1.0.0",
        "benchmark_id": "demo",
        "proposition_id": "demo_v1",
        "semantic_profile_id": "qspecbench.openqasm3.test.v1",
        "tool": {"name": "test", "version": "1", "digest": None},
        "inputs": [
            {
                "path": "artifacts/source.qasm",
                "sha256": "a" * 64,
                "role": "source",
            }
        ],
        "requested_obligations": ["equivalence"],
        "config": {},
        "limits": {"timeout_seconds": 10, "memory_mb": 128, "cpu_seconds": 10},
    }


def _result() -> dict:
    return {
        "schema": "qspecbench.adapter_result.v1",
        "adapter_id": "qspecbench.test.v1",
        "adapter_version": "1.0.0",
        "benchmark_id": "demo",
        "proposition_id": "demo_v1",
        "semantic_profile_id": "qspecbench.openqasm3.test.v1",
        "status": "passing",
        "supported_obligations": ["equivalence"],
        "trust_class": "externally_trusted",
        "tool": {"name": "test", "version": "1", "digest": None},
        "input_hashes": ["a" * 64],
        "result_sha256": None,
        "certificate_sha256": None,
        "started_at": None,
        "finished_at": None,
        "notes": None,
    }


def test_adapter_pair_binds_identity_and_inputs() -> None:
    request = _request()
    result = _result()
    assert validate_adapter_request(request, Path(".")) == []
    assert validate_adapter_result(result, Path("."), request=request) == []


def test_adapter_result_cannot_expand_obligation_scope() -> None:
    request = _request()
    result = _result()
    result["supported_obligations"] = ["equivalence", "hardware_correctness"]
    errors = validate_adapter_result(result, Path("."), request=request)
    assert any("were not requested" in error for error in errors)


def test_adapter_result_must_bind_exact_input_hashes() -> None:
    request = _request()
    result = _result()
    result["input_hashes"] = ["b" * 64]
    errors = validate_adapter_result(result, Path("."), request=request)
    assert any("input_hashes do not exactly match" in error for error in errors)

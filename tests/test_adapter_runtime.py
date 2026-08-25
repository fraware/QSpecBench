"""Regression tests for assurance-backed AdapterRequest/AdapterResult runtime binding."""

from __future__ import annotations

from pathlib import Path

import pytest

from qspecbench.adapter_runtime import AdapterRuntimeError, normalize_adapter_result
from qspecbench.evidence_runner import _check_one_entry
from qspecbench.validate import load_spec

REPO = Path(__file__).resolve().parents[1]
TOFFOLI = REPO / "benchmarks/equivalence/toffoli_decomposition_equivalence"


def _evidence(evidence_id: str) -> dict:
    spec = load_spec(TOFFOLI / "spec.yaml")
    return next(item for item in spec["evidence"] if item["id"] == evidence_id)


def test_auxiliary_qasm_evidence_stays_outside_assurance_protocol() -> None:
    result = _check_one_entry(_evidence("qasm_parse_source"), TOFFOLI, dry_run=True)
    assert result.ok
    assert result.adapter_request is None
    assert result.command is not None
    assert "adapters/qasm/parse_result.py" in result.command.replace("\\", "/")


def test_qcec_runtime_request_binds_proposition_semantics_inputs_and_obligation() -> None:
    result = _check_one_entry(_evidence("qcec_equivalence"), TOFFOLI, dry_run=True)
    assert result.ok
    request = result.adapter_request
    assert request is not None
    assert request["adapter_id"] == "qspecbench.mqt.qcec.v1"
    assert request["adapter_version"] == "1.0.0"
    assert request["benchmark_id"] == "toffoli_decomposition_equivalence"
    assert request["proposition_id"] == "toffoli_decomposition_equivalence_v1"
    assert request["semantic_profile_id"] == "qspecbench.openqasm3.clifford_t_normalized.v1"
    assert request["requested_obligations"] == ["source_target_equivalence"]
    assert [item["role"] for item in request["inputs"]] == ["primary", "secondary"]
    assert [item["path"] for item in request["inputs"]] == [
        "artifacts/source.qasm",
        "artifacts/target.qasm",
    ]
    assert all(len(item["sha256"]) == 64 for item in request["inputs"])


def test_lean_runtime_request_uses_graph_edge_not_evidence_type_guessing() -> None:
    result = _check_one_entry(_evidence("lean_toffoli_pair_bridge"), TOFFOLI, dry_run=True)
    assert result.ok
    request = result.adapter_request
    assert request is not None
    assert request["adapter_id"] == "qspecbench.lean.kernel.v1"
    assert set(request["requested_obligations"]) == {
        "source_artifact_parse",
        "target_artifact_parse",
        "source_denotation",
        "target_denotation",
        "source_target_equivalence",
        "global_phase_policy",
        "wire_order_alignment",
    }


def test_legacy_result_normalization_is_explicitly_request_scoped() -> None:
    dry = _check_one_entry(_evidence("qcec_equivalence"), TOFFOLI, dry_run=True)
    request = dry.adapter_request
    assert request is not None
    result = normalize_adapter_result(
        {"ok": True, "checker": "MQT QCEC", "tool_version": "3.6.0"},
        TOFFOLI,
        request=request,
    )
    assert result["status"] == "passing"
    assert result["supported_obligations"] == ["source_target_equivalence"]
    assert result["trust_class"] == "externally_trusted"
    assert result["input_hashes"] == [item["sha256"] for item in request["inputs"]]
    assert "come from the validated assurance edge/request" in result["notes"]


def test_native_result_cannot_inflate_registered_trust_class() -> None:
    dry = _check_one_entry(_evidence("qcec_equivalence"), TOFFOLI, dry_run=True)
    request = dry.adapter_request
    assert request is not None
    payload = {
        "schema": "qspecbench.adapter_result.v1",
        "adapter_id": request["adapter_id"],
        "adapter_version": request["adapter_version"],
        "benchmark_id": request["benchmark_id"],
        "proposition_id": request["proposition_id"],
        "semantic_profile_id": request["semantic_profile_id"],
        "status": "passing",
        "supported_obligations": request["requested_obligations"],
        "trust_class": "kernel_checked",
        "input_hashes": [item["sha256"] for item in request["inputs"]],
    }
    with pytest.raises(AdapterRuntimeError, match="does not exactly match registered trust class"):
        normalize_adapter_result(payload, TOFFOLI, request=request)

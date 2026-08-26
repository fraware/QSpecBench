from __future__ import annotations

import sys
from pathlib import Path

import pytest

from qspecbench import typed_adapter_registry as registry
from qspecbench.adapter_conformance import shipping_adapter_conformance_errors
from qspecbench.adapter_runtime import AdapterRuntimeError, normalize_adapter_result
from qspecbench.evidence_runner import _default_adapter_command
from qspecbench.evidence_sandbox import run_sandboxed_with_metadata
from qspecbench.typed_adapter_registry import AdapterRegistryError, TypedAdapterSpec

REPO = Path(__file__).resolve().parents[1]


class _FakeEntryPoint:
    def __init__(self, name: str, value: TypedAdapterSpec) -> None:
        self.name = name
        self._value = value

    def load(self) -> TypedAdapterSpec:
        return self._value


def _request(adapter_id: str, adapter_version: str) -> dict:
    return {
        "schema": "qspecbench.adapter_request.v1",
        "adapter_id": adapter_id,
        "adapter_version": adapter_version,
        "benchmark_id": "demo",
        "proposition_id": "demo_v1",
        "semantic_profile_id": "qspecbench.test.v1",
        "tool": {"name": adapter_id, "version": adapter_version, "digest": None},
        "inputs": [
            {
                "path": "artifacts/input.json",
                "sha256": "a" * 64,
                "role": "primary",
            }
        ],
        "requested_obligations": ["demo_obligation"],
        "dependencies": [],
        "expected_outputs": [],
        "config": {"evidence_id": "demo", "evidence_type": "matrix_certificate"},
        "limits": {"timeout_seconds": 30},
    }


def test_all_shipping_adapters_pass_registry_conformance() -> None:
    assert shipping_adapter_conformance_errors(REPO) == []


def test_external_adapter_entry_point_needs_explicit_operator_opt_in(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    spec = TypedAdapterSpec(
        adapter_id="vendor.demo.adapter.v1",
        adapter_version="1.2.3",
        implementation="vendor_demo.adapter",
        trust_ceiling="externally_trusted",
        supported_evidence_types=("simulation",),
        execution_kind="python_module",
    )
    fake = _FakeEntryPoint(spec.adapter_id, spec)
    monkeypatch.setattr(registry, "_entry_points", lambda: (fake,))
    monkeypatch.delenv(registry.PLUGIN_ENABLE_ENV, raising=False)
    registry.clear_external_adapter_cache()
    assert registry.get_typed_adapter(spec.adapter_id) is None

    monkeypatch.setenv(registry.PLUGIN_ENABLE_ENV, "1")
    registry.clear_external_adapter_cache()
    resolved = registry.get_typed_adapter(spec.adapter_id)
    assert resolved == spec
    command = _default_adapter_command(
        "simulation",
        Path("artifact.json"),
        adapter_override=spec.adapter_id,
    )
    assert command is not None
    assert "-m vendor_demo.adapter" in command
    registry.clear_external_adapter_cache()


def test_external_adapter_cannot_shadow_builtin(monkeypatch: pytest.MonkeyPatch) -> None:
    builtin_id = "qspecbench.lean.kernel.v1"
    shadow = TypedAdapterSpec(
        adapter_id=builtin_id,
        adapter_version="999.0.0",
        implementation="malicious.shadow",
        trust_ceiling="externally_trusted",
        supported_evidence_types=("lean_proof",),
        execution_kind="python_module",
    )
    monkeypatch.setenv(registry.PLUGIN_ENABLE_ENV, "1")
    monkeypatch.setattr(registry, "_entry_points", lambda: (_FakeEntryPoint(builtin_id, shadow),))
    registry.clear_external_adapter_cache()
    with pytest.raises(AdapterRegistryError, match="may not shadow"):
        registry.registered_typed_adapters(include_external=True)
    registry.clear_external_adapter_cache()


def test_external_adapter_cannot_self_assign_kernel_trust(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    spec = TypedAdapterSpec(
        adapter_id="vendor.overclaim.adapter.v1",
        adapter_version="1.0.0",
        implementation="vendor_overclaim.adapter",
        trust_ceiling="kernel_checked",
        supported_evidence_types=("simulation",),
        execution_kind="python_module",
    )
    monkeypatch.setenv(registry.PLUGIN_ENABLE_ENV, "1")
    monkeypatch.setattr(registry, "_entry_points", lambda: (_FakeEntryPoint(spec.adapter_id, spec),))
    registry.clear_external_adapter_cache()
    with pytest.raises(AdapterRegistryError, match="exceeds plugin maximum"):
        registry.get_typed_adapter(spec.adapter_id)
    registry.clear_external_adapter_cache()


def test_legacy_result_normalization_hashes_observed_payload_and_runner_metadata() -> None:
    adapter_id = "qspecbench.matrix_certificate.v1"
    request = _request(adapter_id, "1.0.0")
    payload = {
        "ok": True,
        "checker": "matrix-certificate",
        "tool_version": "2.4.1",
        "tool_digest": "c" * 64,
        "certificate_sha256": "b" * 64,
    }
    execution = {
        "wall_time_seconds": 0.125,
        "timed_out": False,
        "exit_code": 0,
        "limits": {
            "timeout_seconds": {"requested": 30, "status": "enforced"},
        },
    }
    result = normalize_adapter_result(
        payload,
        REPO,
        request=request,
        runner_execution=execution,
    )
    assert result["status"] == "passing"
    assert result["trust_class"] == "independently_checkable"
    assert result["tool"] == {
        "name": "matrix-certificate",
        "version": "2.4.1",
        "digest": "c" * 64,
    }
    assert result["certificate_sha256"] == "b" * 64
    assert isinstance(result["result_sha256"], str)
    assert len(result["result_sha256"]) == 64
    assert result["runner_execution"] == execution


def test_adapter_subprocess_cannot_forge_runner_execution() -> None:
    adapter_id = "qspecbench.matrix_certificate.v1"
    request = _request(adapter_id, "1.0.0")
    payload = {
        "schema": "qspecbench.adapter_result.v1",
        "adapter_id": adapter_id,
        "adapter_version": "1.0.0",
        "benchmark_id": "demo",
        "proposition_id": "demo_v1",
        "semantic_profile_id": "qspecbench.test.v1",
        "status": "passing",
        "supported_obligations": ["demo_obligation"],
        "trust_class": "independently_checkable",
        "tool": {"name": "test", "version": "1", "digest": None},
        "input_hashes": ["a" * 64],
        "result_sha256": "d" * 64,
        "certificate_sha256": None,
        "runner_execution": {
            "wall_time_seconds": 0,
            "timed_out": False,
            "exit_code": 0,
            "limits": {
                "timeout_seconds": {"requested": 30, "status": "enforced"},
            },
        },
    }
    with pytest.raises(AdapterRuntimeError, match="may not assert"):
        normalize_adapter_result(payload, REPO, request=request)


def test_sandbox_reports_observed_and_attempted_limits(tmp_path: Path) -> None:
    run = run_sandboxed_with_metadata(
        [sys.executable, "-c", "print('ok')"],
        claim_dir=tmp_path,
        timeout=5,
    )
    metadata = run.runner_execution()
    assert run.process.returncode == 0
    assert metadata["timed_out"] is False
    assert metadata["exit_code"] == 0
    assert metadata["limits"]["timeout_seconds"] == {
        "requested": 5,
        "status": "enforced",
    }
    assert metadata["limits"]["cpu_seconds"]["status"] in {"attempted", "unavailable"}
    assert metadata["limits"]["memory_mb"]["status"] in {"attempted", "unavailable"}

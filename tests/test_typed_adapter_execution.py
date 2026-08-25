"""Execution identity must be typed and independent of descriptive checker strings."""

from __future__ import annotations

import inspect
from pathlib import Path

from qspecbench import evidence_runner
from qspecbench.evidence_adapter_bindings import bound_adapter_id
from qspecbench.evidence_runner import _check_one_entry, _default_adapter_command
from qspecbench.typed_adapter_registry import default_typed_adapter, get_typed_adapter
from qspecbench.validate import load_spec

REPO = Path(__file__).resolve().parents[1]


def test_runner_has_no_checker_string_execution_dispatch() -> None:
    source = inspect.getsource(evidence_runner)
    assert "_DYNAMIC_BRIDGE_CHECKER_SCRIPTS" not in source
    assert "_QEC_STIM_MATCHING_CHECKERS" not in source
    assert "_dynamic_bridge_command" not in source
    assert 'entry.get("checker")' not in source


def test_dynamic_entries_select_typed_semantic_adapters() -> None:
    claim = REPO / "benchmarks/algorithms/teleportation_dynamic_feedforward_protocol"
    spec = load_spec(claim / "spec.yaml")
    evidence = {item["id"]: item for item in spec["evidence"]}
    assert bound_adapter_id(evidence["dynamic_denotation_bridge_verify"], claim) == (
        "qspecbench.bridge.dynamic_denotation.v1"
    )
    assert bound_adapter_id(evidence["dynamic_ast_bridge_verify"], claim) == (
        "qspecbench.bridge.dynamic_ast.v1"
    )
    assert bound_adapter_id(evidence["hardware_isa_abstraction"], claim) == (
        "qspecbench.bridge.hardware_isa.v1"
    )


def test_qec_sidecar_selects_stim_matching_adapter() -> None:
    claim = REPO / "benchmarks/qec/three_qubit_bit_flip_code_corrects_one_x"
    spec = load_spec(claim / "spec.yaml")
    evidence = {item["id"]: item for item in spec["evidence"]}
    for evidence_id in (
        "stim_dem_adapter_result",
        "external_matching_agree",
        "stim_pymatching_dem",
        "stim_pymatching_spacetime_dual",
        "stim_pymatching_bitflip_spacetime_d3_R3",
        "stim_pymatching_bitflip_spacetime_d5_R5",
        "stim_declared_repetition_universe",
        "stim_pymatching_bitflip_spacetime_d7_R7",
    ):
        assert bound_adapter_id(evidence[evidence_id], claim) == (
            "qspecbench.qec.stim_matching.v1"
        )


def test_surface_qec_sidecar_is_execution_authoritative() -> None:
    claim = REPO / "benchmarks/qec/surface_code_distance_three_stabilizer_sanity"
    spec = load_spec(claim / "spec.yaml")
    entry = next(item for item in spec["evidence"] if item["id"] == "stim_declared_surface_universe")
    assert bound_adapter_id(entry, claim) == "qspecbench.qec.stim_matching.v1"
    result = _check_one_entry(entry, claim, dry_run=True)
    assert result.ok
    assert result.command is not None
    assert "adapters/qec/stim_matching_check.py" in result.command.replace("\\", "/")


def test_bitflip_qec_sidecar_is_execution_authoritative() -> None:
    claim = REPO / "benchmarks/qec/three_qubit_bit_flip_code_corrects_one_x"
    spec = load_spec(claim / "spec.yaml")
    entry = next(item for item in spec["evidence"] if item["id"] == "stim_dem_adapter_result")
    result = _check_one_entry(entry, claim, dry_run=True)
    assert result.ok
    assert result.command is not None
    assert "adapters/qec/stim_matching_check.py" in result.command.replace("\\", "/")


def test_typed_adapter_command_uses_registry_implementation_not_checker() -> None:
    command = _default_adapter_command(
        "internal_denotation_consistency",
        Path("artifact.json"),
        adapter_override="qspecbench.bridge.dynamic_denotation.v1",
    )
    assert command is not None
    assert "bridge/dynamic_denotation_check.py" in command.replace("\\", "/")


def test_registry_has_unambiguous_defaults() -> None:
    assert default_typed_adapter("lean_proof").adapter_id == "qspecbench.lean.kernel.v1"
    assert default_typed_adapter("qcec_result").adapter_id == "qspecbench.mqt.qcec.v1"
    assert get_typed_adapter("qspecbench.qec.stim_matching.v1") is not None

"""Dynamic ABRC path + Stim DEM + PyMatching fixture tests."""
from __future__ import annotations

from pathlib import Path

import pytest

from qspecbench.bridge_codegen import (
    DynamicAstMirrorError,
    build_lean_mirror_dynamic_canonical_ast,
    dynamic_ast_sha256_from_qasm,
    lean_mirror_parse_dynamic_line,
)
from qspecbench.bridge_metadata import (
    DYNAMIC_AST_BRIDGE_METADATA,
    DYNAMIC_DENOTATION_BRIDGE_METADATA,
    verify_dynamic_ast_bridge_metadata,
    verify_dynamic_denotation_bridge_metadata,
)
from qspecbench.stim_dem_adapter import StimDemAdapterError, validate_stim_compatible_dem
from qspecbench.verify_dynamic_ast_bridge import (
    verify_dynamic_ast_bridge,
    verify_dynamic_denotation_bridge,
)

REPO = Path(__file__).resolve().parents[1]
FF_QASM = (
    REPO
    / "benchmarks/algorithms/teleportation_preserves_state_up_to_pauli_correction"
    / "artifacts/teleportation_with_feedforward.qasm"
)
SIBLING = REPO / "benchmarks/algorithms/teleportation_dynamic_feedforward_protocol"
QEC = REPO / "benchmarks/qec/three_qubit_bit_flip_code_corrects_one_x"
DEM = QEC / "artifacts/stim_compatible_dem_2x7.json"
GRAPH = QEC / "artifacts/matching_graph_2x7_time_chain.json"
TABLE = QEC / "artifacts/declared_decode_table_2x7.json"


def test_dynamic_ast_mirror_parses_feedforward_measure_if() -> None:
    ast = build_lean_mirror_dynamic_canonical_ast(FF_QASM)
    assert len(ast["gates"]) == 4
    assert ast["measurements"] == [{"cIdx": 0, "qIdx": 0}, {"cIdx": 1, "qIdx": 1}]
    assert ast["controls"] == [
        {"cIdx": 1, "op": "x", "qubits": [2]},
        {"cIdx": 0, "op": "z", "qubits": [2]},
    ]
    assert dynamic_ast_sha256_from_qasm(FF_QASM) == (
        "5bf411e14ed8898bf1af2367911f75ebd46fa659b3dd156500744f7ec2f18654"
    )


def test_dynamic_ast_mirror_fail_closed_on_arrow_measure() -> None:
    with pytest.raises(DynamicAstMirrorError):
        lean_mirror_parse_dynamic_line("measure q[0] -> c[0];")


def test_sibling_dynamic_abrc_verify_passes_without_matrix() -> None:
    if not (SIBLING / "spec.yaml").is_file():
        pytest.skip("sibling dynamic ABRC not packaged")
    result = verify_dynamic_ast_bridge(SIBLING)
    assert result["ok"] is True
    assert result["dynamic_ast_match"] is True
    assert result["matrix_match"] is False
    assert result["claimed_link"] == "kernel_checked_dynamic_ast_semantics"


def test_dynamic_ast_bridge_metadata_pin() -> None:
    errors = verify_dynamic_ast_bridge_metadata(
        "bridge_teleport_dynamic_feedforward_abrc_metadata"
    )
    assert errors == []
    assert (
        DYNAMIC_AST_BRIDGE_METADATA["bridge_teleport_dynamic_feedforward_abrc_metadata"]
        == "teleportation_dynamic_feedforward_protocol"
    )


def test_dynamic_denotation_bridge_metadata_pin() -> None:
    errors = verify_dynamic_denotation_bridge_metadata(
        "bridge_teleport_dynamic_denotation_metadata"
    )
    assert errors == []
    assert (
        DYNAMIC_DENOTATION_BRIDGE_METADATA["bridge_teleport_dynamic_denotation_metadata"]
        == "teleportation_dynamic_feedforward_protocol"
    )


def test_sibling_promoted_to_dynamic_denotation_link() -> None:
    """teleportation_dynamic_feedforward_protocol's claimed_link is the promoted,
    strictly stronger kernel_checked_dynamic_denotation (not a bare AST-hash pin)."""
    if not (SIBLING / "spec.yaml").is_file():
        pytest.skip("sibling dynamic ABRC not packaged")
    result = verify_dynamic_denotation_bridge(SIBLING)
    assert result["ok"] is True
    assert result["denotation_match"] is True
    assert result["dynamic_ast_match"] is True
    assert result["matrix_match"] is False
    assert result["claimed_link"] == "kernel_checked_dynamic_denotation"


def test_stim_dem_adapter_validates_declared_fragment() -> None:
    if not DEM.is_file():
        pytest.skip("DEM artifact not packaged yet")
    result = validate_stim_compatible_dem(DEM)
    assert result["ok"] is True
    assert "fiveFlipS0_R0R1R2R3R4" in result["in_model_faults"]
    assert "six_flipS0_R0R1R2R3R4R5" in result["outside_negatives"]


def test_stim_dem_adapter_rejects_sha_mismatch(tmp_path: Path) -> None:
    if not DEM.is_file():
        pytest.skip("DEM artifact not packaged yet")
    with pytest.raises(StimDemAdapterError, match="sha256 mismatch"):
        validate_stim_compatible_dem(DEM, expected_sha256="0" * 64)


def test_pymatching_fixture_agreement() -> None:
    pymatching = pytest.importorskip("pymatching")
    assert pymatching.__version__ == "2.4.0"
    if not GRAPH.is_file() or not TABLE.is_file():
        pytest.skip("matching fixture artifacts not packaged")
    from qspecbench.pymatching_fixture_adapter import verify_fixture_agreement

    result = verify_fixture_agreement(GRAPH, TABLE)
    assert result["ok"] is True
    assert result["pymatching_invoked"] is True
    assert result["stim_invoked"] is False
    assert result["full_spacetime_mwpm"] is False
    assert "fiveFlipS0_R0R1R2R3R4" in result["agreed_faults"]
    assert result.get("output_sha256")


@pytest.mark.stim
def test_stim_pymatching_dem_agreement() -> None:
    pytest.importorskip("stim")
    pytest.importorskip("pymatching")
    dem = QEC / "artifacts/time_chain_2x7.dem"
    if not dem.is_file() or not TABLE.is_file():
        pytest.skip("Stim DEM artifacts not packaged")
    from qspecbench.stim_pymatching_adapter import STIM_PIN, verify_stim_pymatching_dem

    result = verify_stim_pymatching_dem(dem, TABLE)
    assert result["ok"] is True
    assert result["stim_invoked"] is True
    assert result["pymatching_invoked"] is True
    assert result["full_spacetime_mwpm"] is False
    assert result["stim_version"] == STIM_PIN
    assert "fiveFlipS0_R0R1R2R3R4" in result["agreed_faults"]
    assert "six_flipS0_R0R1R2R3R4R5" in result["outside_checked"]
    assert result.get("dem_sha256")
    assert result.get("output_sha256")


@pytest.mark.stim
def test_stim_pymatching_dual_spacetime_beyond_s0_fragment() -> None:
    pytest.importorskip("stim")
    pytest.importorskip("pymatching")
    dem = QEC / "artifacts/spacetime_2x7_dual.dem"
    table = QEC / "artifacts/declared_decode_table_spacetime_2x7_dual.json"
    if not dem.is_file() or not table.is_file():
        pytest.skip("dual Stim DEM artifacts not packaged")
    from qspecbench.stim_pymatching_adapter import verify_stim_pymatching_dem

    result = verify_stim_pymatching_dem(dem, table)
    assert result["ok"] is True
    assert result["stim_invoked"] is True
    assert result["dem_num_detectors"] == 14
    assert result["full_spacetime_mwpm"] is False
    assert "fiveFlipS1_R0R1R2R3R4" in result["agreed_faults"]
    assert "dual_six_flip_outside" in result["outside_checked"]


def test_dynamic_mirror_broader_if_else_for_while_and_reset() -> None:
    ctrl = lean_mirror_parse_dynamic_line("if (c[1]) x q[2];")
    assert ctrl == ("control", {"cIdx": 1, "op": "x", "qubits": [2]})
    ctrl_t = lean_mirror_parse_dynamic_line("if (c[0] == true) z q[2];")
    assert ctrl_t == ("control", {"cIdx": 0, "op": "z", "qubits": [2]})
    ctrl_else = lean_mirror_parse_dynamic_line("if (c[1] == 1) x q[2] else z q[2];")
    assert ctrl_else == (
        "control",
        {
            "cIdx": 1,
            "op": "x",
            "qubits": [2],
            "elseOp": "z",
            "elseQubits": [2],
        },
    )
    nested = lean_mirror_parse_dynamic_line(
        "if (c[1] == 1) { x q[2]; } else { z q[2]; };"
    )
    assert nested == (
        "control",
        {
            "cIdx": 1,
            "op": "x",
            "qubits": [2],
            "elseOp": "z",
            "elseQubits": [2],
            "nested": True,
        },
    )
    while_fuel = lean_mirror_parse_dynamic_line("while[3] (c[1]) x q[2];")
    assert while_fuel == (
        "control",
        {"cIdx": 1, "op": "x", "qubits": [2], "whileFuel": 3},
    )
    for_gates = lean_mirror_parse_dynamic_line("for i in [0:3] { x q[i]; };")
    assert for_gates == (
        "for_gates",
        {
            "gates": [
                {"op": "x", "qubits": [0]},
                {"op": "x", "qubits": [1]},
                {"op": "x", "qubits": [2]},
            ]
        },
    )
    rst = lean_mirror_parse_dynamic_line("reset q[0];")
    assert rst == ("reset", {"qIdx": 0})
    with pytest.raises(DynamicAstMirrorError):
        lean_mirror_parse_dynamic_line("else x q[0];")
    with pytest.raises(DynamicAstMirrorError):
        lean_mirror_parse_dynamic_line("while (true) x q[0];")
    with pytest.raises(DynamicAstMirrorError):
        lean_mirror_parse_dynamic_line("for i in [0:9] { x q[i]; };")
    with pytest.raises(DynamicAstMirrorError):
        lean_mirror_parse_dynamic_line("while[9] (c[1]) x q[2];")
    with pytest.raises(DynamicAstMirrorError):
        lean_mirror_parse_dynamic_line(
            "if (c[1] == 1) { if (c[0] == 1) { x q[2]; } else { z q[2]; }; } else { y q[2]; };"
        )


def test_matrix_bridge_refuses_measure_if_drop() -> None:
    """Matrix KERNEL_BRIDGE path must fail-closed when QASM has measure/if."""
    from qspecbench.verify_bridge import _qasm_has_measure_or_classical_control

    qasm = (
        REPO
        / "benchmarks/algorithms/teleportation_dynamic_feedforward_protocol"
        / "artifacts/teleportation_with_feedforward.qasm"
    )
    assert _qasm_has_measure_or_classical_control(qasm) is True


def test_dynamic_denotation_link_recognized() -> None:
    from qspecbench.bridge_codegen import (
        DYNAMIC_DENOTATION_LINK,
        is_dynamic_ast_checked_link,
        is_dynamic_denotation_link,
    )

    assert is_dynamic_denotation_link(DYNAMIC_DENOTATION_LINK)
    assert is_dynamic_ast_checked_link(DYNAMIC_DENOTATION_LINK)
    assert not is_dynamic_denotation_link("kernel_checked_dynamic_ast_semantics")


@pytest.mark.stim
def test_stim_pymatching_bitflip_spacetime_d3_R3() -> None:
    pytest.importorskip("stim")
    pytest.importorskip("pymatching")
    dem = QEC / "artifacts/bitflip_spacetime_d3_R3.dem"
    table = QEC / "artifacts/declared_decode_table_bitflip_spacetime_d3_R3.json"
    if not dem.is_file() or not table.is_file():
        pytest.skip("bitflip spacetime DEM not packaged")
    from qspecbench.stim_pymatching_adapter import verify_stim_pymatching_dem

    result = verify_stim_pymatching_dem(dem, table)
    assert result["ok"] is True
    assert result["stim_invoked"] is True
    assert result["dem_num_detectors"] == 8
    assert result["full_spacetime_mwpm"] is False
    assert "none" in result["agreed_faults"]
    assert "all_detectors_outside" in result["outside_checked"]


@pytest.mark.stim
def test_stim_pymatching_bitflip_spacetime_d5_R5() -> None:
    pytest.importorskip("stim")
    pytest.importorskip("pymatching")
    dem = QEC / "artifacts/bitflip_spacetime_d5_R5.dem"
    table = QEC / "artifacts/declared_decode_table_bitflip_spacetime_d5_R5.json"
    if not dem.is_file() or not table.is_file():
        pytest.skip("bitflip spacetime d5 R5 DEM not packaged")
    from qspecbench.stim_pymatching_adapter import verify_stim_pymatching_dem

    result = verify_stim_pymatching_dem(dem, table)
    assert result["ok"] is True
    assert result["stim_invoked"] is True
    assert result["dem_num_detectors"] == 24
    assert result["full_spacetime_mwpm"] is False
    assert "none" in result["agreed_faults"]
    assert "all_detectors_outside" in result["outside_checked"]


@pytest.mark.stim
def test_stim_declared_repetition_universe() -> None:
    pytest.importorskip("stim")
    pytest.importorskip("pymatching")
    from qspecbench.stim_declared_universe_adapter import (
        UNIVERSE_ID,
        verify_declared_repetition_universe,
    )

    result = verify_declared_repetition_universe(QEC / "artifacts")
    assert result["ok"] is True
    assert result["universe_id"] == UNIVERSE_ID
    assert result["full_spacetime_mwpm"] is True
    assert result["full_spacetime_mwpm_scope"] == UNIVERSE_ID
    assert result["unbounded_all_codes_mwpm"] is False
    assert result["unbounded_all_codes_mwpm_status"] == "not_applicable"
    assert len(result["members"]) == 3


@pytest.mark.stim
def test_stim_pymatching_bitflip_spacetime_d7_R7() -> None:
    pytest.importorskip("stim")
    pytest.importorskip("pymatching")
    dem = QEC / "artifacts/bitflip_spacetime_d7_R7.dem"
    table = QEC / "artifacts/declared_decode_table_bitflip_spacetime_d7_R7.json"
    if not dem.is_file() or not table.is_file():
        pytest.skip("bitflip spacetime d7 R7 DEM not packaged")
    from qspecbench.stim_pymatching_adapter import verify_stim_pymatching_dem

    result = verify_stim_pymatching_dem(dem, table)
    assert result["ok"] is True
    assert result["dem_num_detectors"] == 48
    assert result["full_spacetime_mwpm"] is False


def test_hardware_isa_abstraction_fail_closed() -> None:
    from qspecbench.hardware_isa_adapter import (
        HardwareIsaAdapterError,
        verify_hardware_isa_abstraction,
    )

    profile = (
        SIBLING / "artifacts/hardware_isa_profile.json"
        if (SIBLING / "artifacts/hardware_isa_profile.json").is_file()
        else None
    )
    if profile is None:
        pytest.skip("ISA profile not packaged")
    result = verify_hardware_isa_abstraction(profile)
    assert result["ok"] is True
    assert result["hardware_abstraction_isa_layer"] is True
    assert result["hardware_semantics_checked"] is False
    assert result["claims_device_fidelity"] is False
    with pytest.raises(HardwareIsaAdapterError):
        # mutate conceptually: device_live forbidden — use a temp would be heavier;
        # instead ensure adapter rejects claims_device_fidelity via profile check
        bad = profile.read_text(encoding="utf-8").replace(
            '"claims_device_fidelity": false', '"claims_device_fidelity": true'
        )
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "bad.json"
            p.write_text(bad, encoding="utf-8")
            verify_hardware_isa_abstraction(p)

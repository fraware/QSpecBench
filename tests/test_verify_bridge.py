"""Tests for verify-bridge CLI and semantic bridge validation."""

from pathlib import Path

import yaml

from qspecbench.validate import validate_path
from qspecbench.verify_bridge import verify_bridge, write_bridge_result

REPO = Path(__file__).resolve().parents[1]

KERNEL_CHECKED = [
    "benchmarks/equivalence/cnot_self_inverse_cancellation",
    "benchmarks/equivalence/hadamard_conjugates_x_to_z",
    "benchmarks/equivalence/single_qubit_gate_cancellation",
    "benchmarks/equivalence/qft_inverse_qft_small_instance",
    "benchmarks/equivalence/clifford_simplification_preserves_unitary",
    "benchmarks/equivalence/source_optimized_qasm_equivalence_small_instance",
    "benchmarks/equivalence/phase_polynomial_equivalence_small_instance",
    "benchmarks/algorithms/teleportation_preserves_state_up_to_pauli_correction",
    "benchmarks/equivalence/rx_gate_equivalence_small_instance",
    "benchmarks/algorithms/bell_state_preparation",
]


def test_verify_bridge_kernel_checked_benchmarks():
    for rel in KERNEL_CHECKED:
        claim = REPO / rel
        result = write_bridge_result(claim)
        assert result["ok"], f"bridge verify failed for {rel}: {result.get('errors')}"


def test_verify_bridge_reads_semantic_bridge():
    claim = REPO / KERNEL_CHECKED[0]
    result = verify_bridge(claim)
    assert result["claimed_link"] == "kernel_checked"
    assert "lean_module" in result


def test_kernel_checked_validates_with_bridge_evidence():
    claim = REPO / KERNEL_CHECKED[0]
    spec_path = claim / "spec.yaml"
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    assert any(e.get("id") == "bridge_verify" for e in spec.get("evidence", []))
    results = validate_path(claim)
    assert results and results[0].ok

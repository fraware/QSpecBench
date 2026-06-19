#!/usr/bin/env python3
"""Add proof_obligations to reference benchmarks (idempotent)."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]

OBLIGATIONS: dict[str, list[dict[str, str]]] = {
    "no_cloning_negative_claim": [
        {"id": "impossibility_scaffold", "status": "passing", "notes": "Lean matrix no-cloning obstruction"},
        {"id": "full_hilbert_space_model", "status": "not_applicable", "notes": "Finite matrix scaffold only"},
    ],
    "teleportation_preserves_state_up_to_pauli_correction": [
        {"id": "unitary_scaffold", "status": "passing", "notes": "Lean teleportation_preserves_state anchor"},
        {"id": "qasm_lean_bridge", "status": "passing", "notes": "Bell-prep scaffold kernel_checked via verify-bridge"},
        {"id": "relational_protocol", "status": "partial", "notes": "Measurements and Pauli corrections not kernel-checked"},
    ],
    "cnot_self_inverse_cancellation": [
        {"id": "lean_kernel_proof", "status": "passing", "notes": "cnot_mul_self on 4x4 model"},
        {"id": "semantic_bridge", "status": "passing", "notes": "kernel_checked verify-bridge"},
        {"id": "openqasm_full_language", "status": "not_applicable", "notes": "Gate-subset denotation only"},
    ],
    "hadamard_conjugates_x_to_z": [
        {"id": "lean_kernel_proof", "status": "passing", "notes": "Hadamard conjugation on int model"},
        {"id": "semantic_bridge", "status": "passing", "notes": "kernel_checked verify-bridge"},
    ],
    "single_qubit_gate_cancellation": [
        {"id": "lean_kernel_proof", "status": "passing", "notes": "Hadamard cancellation"},
        {"id": "semantic_bridge", "status": "passing", "notes": "kernel_checked verify-bridge"},
    ],
    "qft_inverse_qft_small_instance": [
        {"id": "lean_kernel_proof", "status": "passing", "notes": "QFT2 inverse scaffold"},
        {"id": "semantic_bridge", "status": "passing", "notes": "kernel_checked verify-bridge"},
    ],
    "clifford_simplification_preserves_unitary": [
        {"id": "lean_kernel_proof", "status": "passing", "notes": "Clifford simplification anchor"},
        {"id": "semantic_bridge", "status": "passing", "notes": "kernel_checked verify-bridge"},
    ],
    "steane_code_stabilizer_commutation": [
        {"id": "stabilizer_commutation", "status": "passing", "notes": "Lean steane_stabilizers_commute"},
        {"id": "decoder_correctness", "status": "not_applicable", "notes": "Decoder out of scope"},
    ],
    "three_qubit_bit_flip_code_corrects_one_x": [
        {"id": "stabilizer_commutation", "status": "passing", "notes": "Bit-flip stabilizer commutation"},
        {"id": "decoder_correctness", "status": "not_applicable", "notes": "Decoder assumed per trust boundary"},
        {"id": "correction_claim", "status": "partial", "notes": "Correction tables not kernel-checked"},
    ],
    "three_qubit_phase_flip_code_corrects_one_z": [
        {"id": "stabilizer_commutation", "status": "passing", "notes": "Phase-flip stabilizer commutation"},
        {"id": "decoder_correctness", "status": "not_applicable", "notes": "Decoder assumed per trust boundary"},
    ],
    "small_fermionic_hamiltonian_is_hermitian": [
        {"id": "hermiticity", "status": "passing", "notes": "Mathlib Hermitian proof on declared Pauli sum"},
        {"id": "jw_mapping", "status": "partial", "notes": "Jordan-Wigner mapping not fully checked"},
    ],
    "formalize_no_cloning_statement": [
        {"id": "kernel_anchor", "status": "passing", "notes": "Links to QSpecBench.NoCloning library theorem"},
        {"id": "draft_faithfulness", "status": "partial", "notes": "AI draft untrusted; rubric score 4"},
    ],
}


def main() -> int:
    updated = 0
    for spec_path in (REPO / "benchmarks").rglob("spec.yaml"):
        if "_template" in spec_path.parts:
            continue
        spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        if spec.get("status", {}).get("maturity") != "reference":
            continue
        bid = spec.get("id")
        if bid not in OBLIGATIONS:
            print(f"skip (no template): {bid}")
            continue
        if spec.get("proof_obligations") == OBLIGATIONS[bid]:
            continue
        spec["qspecbench_version"] = "0.2"
        spec["proof_obligations"] = OBLIGATIONS[bid]
        spec_path.write_text(yaml.dump(spec, sort_keys=False, default_flow_style=False), encoding="utf-8")
        updated += 1
        print(f"updated {spec_path.relative_to(REPO)}")
    print(f"patched {updated} reference spec(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# QSpecBench Dashboard

Auto-generated benchmark status overview.

## Summary

- **Total benchmarks:** 48
- **By track:** ai_formalization: 7, algorithms: 10, equivalence: 10, hamiltonian: 8, qec: 13
- **By maturity:** reference: 42, usable: 6
- **With checked evidence:** 44
- **With partial evidence:** 4
- **With no evidence:** 0
- **With AI draft evidence:** 7
- **With approximate specifications:** 2
- **QEC claims:** 13
- **With resource contracts:** 11
- **Kernel-checked semantic bridges:** 14

### Passing evidence by trust level

- **checked:** 40
- **independently_checkable:** 3
- **externally_trusted:** 60
- **heuristic:** 8

### Reference coverage by track

- **ai_formalization:** 5
- **algorithms:** 9
- **equivalence:** 10
- **hamiltonian:** 7
- **qec:** 11

## Benchmarks

| ID | Track | Claim type | Difficulty | Maturity | Evidence | CI | Trust summary |
|---|---|---|---|---|---|---|---|
| extract_teleportation_correctness_statement | ai_formalization | formalization_faithfulness | intermediate | reference | lean_proof, human_review | passing | trusted kernel: Lean 4 kernel |
| formalize_bit_flip_code_corrects_one_x | ai_formalization | formalization_faithfulness | intermediate | reference | lean_proof, human_review | passing | trusted kernel: Lean 4 kernel |
| formalize_no_cloning_statement | ai_formalization | formalization_faithfulness | introductory | reference | lean_proof, human_review | passing | trusted kernel: Lean 4 kernel |
| formalize_qec_distance_claim_statement | ai_formalization | formalization | intermediate | usable | lean_proof | passing | trusted kernel: Lean 4 kernel |
| formalize_small_hamiltonian_hermiticity_statement | ai_formalization | formalization_faithfulness | intermediate | reference | lean_proof, human_review | passing | trusted kernel: Lean 4 kernel |
| formalize_stabilizer_commutation_statement | ai_formalization | formalization_faithfulness | intermediate | reference | lean_proof, human_review | passing | trusted kernel: Lean 4 kernel |
| formalize_teleportation_spec_statement | ai_formalization | formalization | intermediate | usable | lean_proof | passing | trusted kernel: Lean 4 kernel |
| amplitude_damping_channel_specification | algorithms | channel_specification | intermediate | usable | simulation | passing | checked components present |
| bell_state_preparation | algorithms | state_preparation | introductory | reference | qasm_parse, lean_proof... | passing | trusted kernel: Lean 4 kernel |
| deutsch_jozsa_constant_balanced_distinction | algorithms | oracle_distinction | intermediate | reference | qasm_parse, lean_proof | passing | trusted kernel: Lean 4 kernel |
| grover_single_iteration_amplitude_amplification | algorithms | amplitude_amplification | intermediate | reference | qasm_parse, lean_proof | passing | trusted kernel: Lean 4 kernel |
| no_cloning_negative_claim | algorithms | negative_claim | frontier | reference | lean_proof | passing | trusted kernel: Lean 4 kernel |
| phase_estimation_exact_eigenphase_small_instance | algorithms | eigenphase_estimation | frontier | reference | qasm_parse, lean_proof | passing | trusted kernel: Lean 4 kernel |
| qft_then_inverse_qft_identity_up_to_ordering | algorithms | algorithm_identity | intermediate | reference | qasm_parse, lean_proof... | passing | trusted kernel: Lean 4 kernel |
| superdense_coding_decodes_two_classical_bits | algorithms | protocol_correctness | introductory | reference | qasm_parse, lean_proof | passing | trusted kernel: Lean 4 kernel |
| swap_from_three_cx | algorithms | circuit_construction | introductory | reference | qasm_parse, qasm_parse... | passing | trusted kernel: Lean 4 kernel |
| teleportation_preserves_state_up_to_pauli_correction | algorithms | protocol_correctness | introductory | reference | qasm_parse, lean_proof... | passing | trusted kernel: Lean 4 kernel |
| circuit_identity_after_layout | equivalence | unitary_equivalence | introductory | reference | qasm_parse, qasm_parse... | passing | trusted kernel: Lean 4 kernel |
| clifford_simplification_preserves_unitary | equivalence | unitary_equivalence | advanced | reference | qasm_parse, qasm_parse... | passing | trusted kernel: Lean 4 kernel |
| cnot_self_inverse_cancellation | equivalence | unitary_equivalence | introductory | reference | qasm_parse, qasm_parse... | passing | trusted kernel: Lean 4 kernel |
| hadamard_conjugates_x_to_z | equivalence | unitary_equivalence | intermediate | reference | lean_proof, qasm_parse... | passing | trusted kernel: Lean 4 kernel |
| phase_polynomial_equivalence_small_instance | equivalence | unitary_equivalence | intermediate | reference | qasm_parse, qasm_parse... | passing | trusted kernel: Lean 4 kernel |
| qft_inverse_qft_small_instance | equivalence | unitary_equivalence | intermediate | reference | qasm_parse, qasm_parse... | passing | trusted kernel: Lean 4 kernel |
| rx_gate_equivalence_small_instance | equivalence | unitary_equivalence | introductory | reference | lean_proof, qasm_parse... | passing | trusted kernel: Lean 4 kernel |
| single_qubit_gate_cancellation | equivalence | unitary_equivalence | introductory | reference | lean_proof, qasm_parse... | passing | trusted kernel: Lean 4 kernel |
| source_optimized_qasm_equivalence_small_instance | equivalence | unitary_equivalence | intermediate | reference | qasm_parse, qasm_parse... | passing | trusted kernel: Lean 4 kernel |
| toffoli_decomposition_equivalence | equivalence | unitary_equivalence | intermediate | reference | qasm_parse, qasm_parse... | passing | trusted kernel: Lean 4 kernel |
| bravyi_kitaev_small_instance | hamiltonian | mapping_sanity | intermediate | usable | simulation | passing | checked components present |
| heisenberg_model_hermiticity_small_instance | hamiltonian | hermiticity | introductory | reference | simulation, lean_proof | passing | trusted kernel: Lean 4 kernel |
| jordan_wigner_preserves_anticommutation_small_instance | hamiltonian | hamiltonian_claim | intermediate | reference | simulation, lean_proof | passing | trusted kernel: Lean 4 kernel |
| pauli_decomposition_matches_source_hamiltonian_small_instance | hamiltonian | hamiltonian_claim | advanced | reference | simulation, lean_proof | passing | trusted kernel: Lean 4 kernel |
| resource_contract_for_small_hamiltonian_simulation | hamiltonian | hamiltonian_claim | intermediate | reference | simulation, lean_proof | passing | trusted kernel: Lean 4 kernel |
| single_trotter_step_declares_error_contract | hamiltonian | hamiltonian_claim | intermediate | reference | lean_proof, human_review | passing | trusted kernel: Lean 4 kernel |
| small_fermionic_hamiltonian_is_hermitian | hamiltonian | hermiticity | introductory | reference | simulation, lean_proof | passing | trusted kernel: Lean 4 kernel |
| trotter_second_order_bound_contract | hamiltonian | error_bound_contract | intermediate | reference | lean_proof, human_review | passing | trusted kernel: Lean 4 kernel |
| bb84_sifted_key_partial_claim | qec | protocol_claim | intermediate | usable | human_review | passing | checked components present |
| detector_model_sanity_check | qec | model_sanity | introductory | usable | simulation | passing | checked components present |
| distance_certificate_small_css_code | qec | qec_claim | intermediate | reference | qec_verifier_result, smt_certificate | passing | checked components present |
| logical_state_preserved_up_to_pauli_frame | qec | qec_claim | advanced | reference | qec_verifier_result, lean_proof | passing | trusted kernel: Lean 4 kernel |
| repeated_round_qec_temporal_specification | qec | qec_claim | intermediate | reference | qec_verifier_result, lean_proof | passing | trusted kernel: Lean 4 kernel |
| repetition_code_three_one_three | qec | qec_claim | introductory | reference | qec_verifier_result, lean_proof | passing | trusted kernel: Lean 4 kernel |
| shor_code_stabilizer_commutation | qec | stabilizer_commutation | intermediate | reference | qec_verifier_result, lean_proof | passing | trusted kernel: Lean 4 kernel |
| steane_code_stabilizer_commutation | qec | qec_claim | intermediate | reference | qec_verifier_result, lean_proof | passing | trusted kernel: Lean 4 kernel |
| surface_code_distance_three_stabilizer_sanity | qec | qec_claim | intermediate | reference | qec_verifier_result, lean_proof | passing | trusted kernel: Lean 4 kernel |
| surface_code_single_pauli_error_correction | qec | qec_claim | intermediate | reference | qec_verifier_result, lean_proof | passing | trusted kernel: Lean 4 kernel |
| surface_code_single_round_syndrome_extraction | qec | qec_claim | intermediate | reference | qec_verifier_result, lean_proof | passing | trusted kernel: Lean 4 kernel |
| three_qubit_bit_flip_code_corrects_one_x | qec | error_correction | intermediate | reference | qec_verifier_result, lean_proof | passing | trusted kernel: Lean 4 kernel |
| three_qubit_phase_flip_code_corrects_one_z | qec | error_correction | intermediate | reference | qec_verifier_result, lean_proof | passing | trusted kernel: Lean 4 kernel |

# QSpecBench Dashboard

Auto-generated benchmark status overview.

## Summary

- **Total benchmarks:** 48
- **By track:** ai_formalization: 7, algorithms: 10, equivalence: 10, hamiltonian: 8, qec: 13
- **By maturity:** reference: 18, usable: 30
- **With checked evidence:** 21
- **With partial evidence:** 27
- **With no evidence:** 0
- **With AI draft evidence:** 7
- **With approximate specifications:** 2
- **QEC claims:** 13
- **With resource contracts:** 11
- **Kernel-checked semantic bridges:** 8

### Passing evidence by trust level

- **checked:** 20
- **independently_checkable:** 3
- **externally_trusted:** 55
- **heuristic:** 8

### Reference coverage by track

- **ai_formalization:** 4
- **algorithms:** 2
- **equivalence:** 7
- **hamiltonian:** 1
- **qec:** 4

## Benchmarks

| ID | Track | Claim type | Difficulty | Maturity | Evidence | CI | Trust summary |
|---|---|---|---|---|---|---|---|
| extract_teleportation_correctness_statement | ai_formalization | formalization_faithfulness | intermediate | usable | lean_proof | passing | trusted kernel: Lean 4 kernel |
| formalize_bit_flip_code_corrects_one_x | ai_formalization | formalization_faithfulness | intermediate | reference | lean_proof, human_review | passing | trusted kernel: Lean 4 kernel |
| formalize_no_cloning_statement | ai_formalization | formalization_faithfulness | introductory | reference | lean_proof, human_review | passing | trusted kernel: Lean 4 kernel |
| formalize_qec_distance_claim_statement | ai_formalization | formalization | intermediate | usable | lean_proof | passing | trusted kernel: Lean 4 kernel |
| formalize_small_hamiltonian_hermiticity_statement | ai_formalization | formalization_faithfulness | intermediate | reference | lean_proof, human_review | passing | trusted kernel: Lean 4 kernel |
| formalize_stabilizer_commutation_statement | ai_formalization | formalization_faithfulness | intermediate | reference | lean_proof, human_review | passing | trusted kernel: Lean 4 kernel |
| formalize_teleportation_spec_statement | ai_formalization | formalization | intermediate | usable | lean_proof | passing | trusted kernel: Lean 4 kernel |
| amplitude_damping_channel_specification | algorithms | channel_specification | intermediate | usable | simulation | passing | checked components present |
| bell_state_preparation | algorithms | state_preparation | introductory | usable | qasm_parse | passing | checked components present |
| deutsch_jozsa_constant_balanced_distinction | algorithms | oracle_distinction | intermediate | usable | qasm_parse | passing | checked components present |
| grover_single_iteration_amplitude_amplification | algorithms | amplitude_amplification | intermediate | usable | qasm_parse | passing | checked components present |
| no_cloning_negative_claim | algorithms | negative_claim | frontier | reference | lean_proof | passing | trusted kernel: Lean 4 kernel |
| phase_estimation_exact_eigenphase_small_instance | algorithms | eigenphase_estimation | frontier | usable | qasm_parse | passing | checked components present |
| qft_then_inverse_qft_identity_up_to_ordering | algorithms | algorithm_identity | intermediate | usable | qasm_parse | passing | checked components present |
| superdense_coding_decodes_two_classical_bits | algorithms | protocol_correctness | introductory | usable | qasm_parse | passing | checked components present |
| swap_from_three_cx | algorithms | circuit_construction | introductory | usable | qasm_parse, qasm_parse... | passing | checked components present |
| teleportation_preserves_state_up_to_pauli_correction | algorithms | protocol_correctness | introductory | reference | qasm_parse, lean_proof... | passing | trusted kernel: Lean 4 kernel |
| circuit_identity_after_layout | equivalence | unitary_equivalence | introductory | usable | qasm_parse, qasm_parse... | passing | checked components present |
| clifford_simplification_preserves_unitary | equivalence | unitary_equivalence | advanced | reference | qasm_parse, qasm_parse... | passing | trusted kernel: Lean 4 kernel |
| cnot_self_inverse_cancellation | equivalence | unitary_equivalence | introductory | reference | qasm_parse, qasm_parse... | passing | trusted kernel: Lean 4 kernel |
| hadamard_conjugates_x_to_z | equivalence | unitary_equivalence | intermediate | reference | lean_proof, qasm_parse... | passing | trusted kernel: Lean 4 kernel |
| phase_polynomial_equivalence_small_instance | equivalence | unitary_equivalence | intermediate | reference | qasm_parse, qasm_parse... | passing | trusted kernel: Lean 4 kernel |
| qft_inverse_qft_small_instance | equivalence | unitary_equivalence | intermediate | reference | qasm_parse, qasm_parse... | passing | trusted kernel: Lean 4 kernel |
| rx_gate_equivalence_small_instance | equivalence | unitary_equivalence | introductory | usable | qasm_parse, qasm_parse... | passing | checked components present |
| single_qubit_gate_cancellation | equivalence | unitary_equivalence | introductory | reference | lean_proof, qasm_parse... | passing | trusted kernel: Lean 4 kernel |
| source_optimized_qasm_equivalence_small_instance | equivalence | unitary_equivalence | intermediate | reference | qasm_parse, qasm_parse... | passing | trusted kernel: Lean 4 kernel |
| toffoli_decomposition_equivalence | equivalence | unitary_equivalence | intermediate | usable | qasm_parse, qasm_parse... | passing | checked components present |
| bravyi_kitaev_small_instance | hamiltonian | mapping_sanity | intermediate | usable | simulation | passing | checked components present |
| heisenberg_model_hermiticity_small_instance | hamiltonian | hermiticity | introductory | usable | simulation | passing | checked components present |
| jordan_wigner_preserves_anticommutation_small_instance | hamiltonian | hamiltonian_claim | intermediate | usable | simulation | passing | checked components present |
| pauli_decomposition_matches_source_hamiltonian_small_instance | hamiltonian | hamiltonian_claim | advanced | usable | simulation | passing | checked components present |
| resource_contract_for_small_hamiltonian_simulation | hamiltonian | hamiltonian_claim | intermediate | usable | simulation | passing | checked components present |
| single_trotter_step_declares_error_contract | hamiltonian | hamiltonian_claim | intermediate | usable | partial | passing | human review only |
| small_fermionic_hamiltonian_is_hermitian | hamiltonian | hermiticity | introductory | reference | simulation, lean_proof | passing | trusted kernel: Lean 4 kernel |
| trotter_second_order_bound_contract | hamiltonian | error_bound_contract | intermediate | usable | partial | passing | human review only |
| bb84_sifted_key_partial_claim | qec | protocol_claim | intermediate | usable | partial | passing | human review only |
| detector_model_sanity_check | qec | model_sanity | introductory | usable | simulation | passing | checked components present |
| distance_certificate_small_css_code | qec | qec_claim | intermediate | reference | qec_verifier_result, smt_certificate | passing | checked components present |
| logical_state_preserved_up_to_pauli_frame | qec | qec_claim | advanced | usable | qec_verifier_result | passing | checked components present |
| repeated_round_qec_temporal_specification | qec | qec_claim | intermediate | usable | qec_verifier_result | passing | checked components present |
| repetition_code_three_one_three | qec | qec_claim | introductory | usable | qec_verifier_result | passing | checked components present |
| shor_code_stabilizer_commutation | qec | stabilizer_commutation | intermediate | usable | qec_verifier_result | passing | checked components present |
| steane_code_stabilizer_commutation | qec | qec_claim | intermediate | reference | qec_verifier_result, lean_proof | passing | trusted kernel: Lean 4 kernel |
| surface_code_distance_three_stabilizer_sanity | qec | qec_claim | intermediate | usable | qec_verifier_result | passing | checked components present |
| surface_code_single_pauli_error_correction | qec | qec_claim | intermediate | usable | qec_verifier_result | passing | checked components present |
| surface_code_single_round_syndrome_extraction | qec | qec_claim | intermediate | usable | qec_verifier_result | passing | checked components present |
| three_qubit_bit_flip_code_corrects_one_x | qec | error_correction | intermediate | reference | qec_verifier_result, lean_proof | passing | trusted kernel: Lean 4 kernel |
| three_qubit_phase_flip_code_corrects_one_z | qec | error_correction | intermediate | reference | qec_verifier_result, lean_proof | passing | trusted kernel: Lean 4 kernel |

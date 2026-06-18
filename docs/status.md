# QSpecBench Dashboard

Auto-generated benchmark status overview.

## Summary

- **Total benchmarks:** 34
- **By track:** ai_formalization: 5, algorithms: 7, equivalence: 7, hamiltonian: 5, qec: 10
- **By maturity:** reference: 1, seed: 21, usable: 12
- **With checked evidence:** 3
- **With partial evidence:** 11
- **With no evidence:** 20
- **With AI draft evidence:** 1
- **With approximate specifications:** 1
- **QEC claims:** 10
- **With resource contracts:** 6

## Benchmarks

| ID | Track | Claim type | Difficulty | Maturity | Evidence | CI | Trust summary |
|---|---|---|---|---|---|---|---|
| extract_teleportation_correctness_statement | ai_formalization | formalization_faithfulness | intermediate | seed | none | passing | no kernel proof |
| formalize_bit_flip_code_corrects_one_x | ai_formalization | formalization_faithfulness | intermediate | seed | none | passing | no kernel proof |
| formalize_no_cloning_statement | ai_formalization | formalization_faithfulness | introductory | usable | partial | passing | checked components present |
| formalize_small_hamiltonian_hermiticity_statement | ai_formalization | formalization_faithfulness | intermediate | seed | none | passing | no kernel proof |
| formalize_stabilizer_commutation_statement | ai_formalization | formalization_faithfulness | intermediate | seed | none | passing | no kernel proof |
| deutsch_jozsa_constant_balanced_distinction | algorithms | oracle_distinction | intermediate | usable | qasm_parse | passing | checked components present |
| grover_single_iteration_amplitude_amplification | algorithms | amplitude_amplification | intermediate | seed | none | passing | no kernel proof |
| no_cloning_negative_claim | algorithms | negative_claim | introductory | seed | partial | passing | human review only |
| phase_estimation_exact_eigenphase_small_instance | algorithms | eigenphase_estimation | frontier | seed | none | passing | no kernel proof |
| qft_then_inverse_qft_identity_up_to_ordering | algorithms | algorithm_identity | intermediate | seed | none | passing | no kernel proof |
| superdense_coding_decodes_two_classical_bits | algorithms | protocol_correctness | introductory | usable | qasm_parse | passing | checked components present |
| teleportation_preserves_state_up_to_pauli_correction | algorithms | protocol_correctness | introductory | usable | qasm_parse | passing | checked components present |
| clifford_simplification_preserves_unitary | equivalence | unitary_equivalence | intermediate | seed | none | passing | no kernel proof |
| cnot_self_inverse_cancellation | equivalence | unitary_equivalence | introductory | reference | qasm_parse, qasm_parse... | passing | trusted kernel: Lean 4 kernel |
| hadamard_conjugates_x_to_z | equivalence | unitary_equivalence | intermediate | usable | lean_proof, qasm_parse... | passing | trusted kernel: Lean 4 kernel |
| phase_polynomial_equivalence_small_instance | equivalence | unitary_equivalence | intermediate | seed | none | passing | no kernel proof |
| qft_inverse_qft_small_instance | equivalence | unitary_equivalence | intermediate | usable | qasm_parse, qasm_parse | passing | checked components present |
| single_qubit_gate_cancellation | equivalence | unitary_equivalence | introductory | usable | lean_proof, qasm_parse... | passing | trusted kernel: Lean 4 kernel |
| source_optimized_qasm_equivalence_small_instance | equivalence | unitary_equivalence | intermediate | seed | none | passing | no kernel proof |
| jordan_wigner_preserves_anticommutation_small_instance | hamiltonian | hamiltonian_claim | intermediate | seed | none | passing | no kernel proof |
| pauli_decomposition_matches_source_hamiltonian_small_instance | hamiltonian | hamiltonian_claim | intermediate | seed | none | passing | no kernel proof |
| resource_contract_for_small_hamiltonian_simulation | hamiltonian | hamiltonian_claim | intermediate | seed | none | passing | no kernel proof |
| single_trotter_step_declares_error_contract | hamiltonian | hamiltonian_claim | intermediate | usable | partial | passing | human review only |
| small_fermionic_hamiltonian_is_hermitian | hamiltonian | hermiticity | introductory | usable | simulation | passing | checked components present |
| distance_certificate_small_css_code | qec | qec_claim | intermediate | seed | none | passing | no kernel proof |
| logical_state_preserved_up_to_pauli_frame | qec | qec_claim | intermediate | seed | none | passing | no kernel proof |
| repeated_round_qec_temporal_specification | qec | qec_claim | intermediate | seed | none | passing | no kernel proof |
| shor_code_stabilizer_commutation | qec | stabilizer_commutation | intermediate | usable | qec_verifier_result | passing | checked components present |
| steane_code_stabilizer_commutation | qec | qec_claim | intermediate | seed | none | passing | no kernel proof |
| surface_code_distance_three_stabilizer_sanity | qec | qec_claim | intermediate | seed | none | passing | no kernel proof |
| surface_code_single_pauli_error_correction | qec | qec_claim | intermediate | seed | none | passing | no kernel proof |
| surface_code_single_round_syndrome_extraction | qec | qec_claim | intermediate | seed | none | passing | no kernel proof |
| three_qubit_bit_flip_code_corrects_one_x | qec | error_correction | intermediate | usable | qec_verifier_result | passing | checked components present |
| three_qubit_phase_flip_code_corrects_one_z | qec | error_correction | intermediate | usable | qec_verifier_result | passing | checked components present |

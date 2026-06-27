# QSpecBench Dashboard

Auto-generated benchmark status overview.

Evidence headline note: most reference-scaffold benchmarks demonstrate the QSpecBench evidence format and trust-boundary discipline; a checked headline claim is reserved for `reference_claim` benchmarks whose full informal claim is proved.

## Versions

- **Schema:** 0.2
- **Tooling:** 0.2.0
- **Corpus:** 0.1.0
- **Release tag:** v0.1.0

## Summary

- **Total benchmarks:** 48
- **By track:** ai_formalization: 7, algorithms: 10, equivalence: 10, hamiltonian: 8, qec: 13
- **By maturity:** reference_claim: 8, reference_contract: 2, reference_scaffold: 30, seed: 1, usable: 7
- **With any checked evidence:** 44
- **With headline claim checked (reference_claim or checked headline):** 8
- **With scaffold-only checked evidence:** 36
- **With unchecked headline assumptions:** 40
- **With partial (non-checked) evidence only:** 4
- **With no evidence:** 0
- **With AI draft evidence:** 7
- **With approximate specifications:** 2
- **QEC claims:** 13
- **With resource contracts:** 11
- **Manifest-checked theorem bindings:** 11
- **Python denotation consistency checks:** 3
- **Kernel-checked artifact semantics bridges:** 0
- **Documented (not proved) bridges:** 4

### Passing evidence by trust level

- **checked:** 43
- **independently_checkable:** 17
- **externally_trusted:** 62
- **heuristic:** 8

### Reference-scaffold coverage by track

- **ai_formalization:** 5
- **algorithms:** 9
- **equivalence:** 10
- **hamiltonian:** 7
- **qec:** 9

## Benchmarks

| ID | Track | Claim type | Difficulty | Maturity | Evidence | CI | Trust summary |
|---|---|---|---|---|---|---|---|
| extract_teleportation_correctness_statement | ai_formalization | formalization_faithfulness | intermediate | reference_scaffold | lean_proof, human_review | passing | proof_scope: fragment; headline: partially_checked; checked: Lean; unchecked: full_protocol, full_faithfulness_of_ai_draft_text_to_source_phr, general_state_teleportation_beyond_computational, +1 more |
| formalize_bit_flip_code_corrects_one_x | ai_formalization | formalization_faithfulness | intermediate | reference_scaffold | lean_proof, human_review | passing | proof_scope: fragment; headline: partially_checked; checked: Lean; unchecked: draft_faithfulness, full_faithfulness_of_ai_draft_text_to_source_phr |
| formalize_no_cloning_statement | ai_formalization | formalization_faithfulness | introductory | reference_scaffold | lean_proof, human_review | passing | proof_scope: fragment; headline: partially_checked; checked: Lean; unchecked: draft_faithfulness, full_faithfulness_of_ai_draft_text_to_source_phr |
| formalize_qec_distance_claim_statement | ai_formalization | formalization | intermediate | usable | lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean; unchecked: full_faithfulness_of_ai_draft_text_to_source_phr |
| formalize_small_hamiltonian_hermiticity_statement | ai_formalization | formalization_faithfulness | intermediate | reference_scaffold | lean_proof, human_review | passing | proof_scope: fragment; headline: partially_checked; checked: Lean; unchecked: draft_faithfulness, full_faithfulness_of_ai_draft_text_to_source_phr |
| formalize_stabilizer_commutation_statement | ai_formalization | formalization_faithfulness | intermediate | reference_scaffold | lean_proof, human_review | passing | proof_scope: fragment; headline: partially_checked; checked: Lean; unchecked: draft_faithfulness, full_faithfulness_of_ai_draft_text_to_source_phr |
| formalize_teleportation_spec_statement | ai_formalization | formalization | intermediate | usable | lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean; unchecked: full_faithfulness_of_ai_draft_text_to_source_phr |
| amplitude_damping_channel_specification | algorithms | channel_specification | intermediate | usable | simulation | passing | proof_scope: syntax_or_review; headline: unproved; checked: declared checks; unchecked: simulation_heuristic, cptp_property_proof |
| bell_state_preparation | algorithms | state_preparation | introductory | reference_claim | qasm_parse, lean_proof... | passing | proof_scope: full; headline: checked; checked_under: qspecbench.openqasm3.int_scaffold.v0, finite_matrix_model; not_checked: full_openqasm3, hardware_semantics; checked: Lean, QASM syntax, Python bridge; unchecked: openqasm_h_normalization_links_integer_model_to_, global_phase_of_phi_state |
| deutsch_jozsa_constant_balanced_distinction | algorithms | oracle_distinction | intermediate | reference_scaffold | qasm_parse, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QASM syntax; unchecked: oracle_distinction, dj_correctness_for_constant_vs_balanced |
| grover_single_iteration_amplitude_amplification | algorithms | amplitude_amplification | intermediate | reference_scaffold | qasm_parse, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QASM syntax; unchecked: amplitude_lift, semantic_correctness_of_circuit_vs_claim |
| no_cloning_negative_claim | algorithms | negative_claim | frontier | reference_scaffold | lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean; unchecked: full_universal_cloner_formalization_beyond_basis |
| phase_estimation_exact_eigenphase_small_instance | algorithms | eigenphase_estimation | frontier | reference_scaffold | qasm_parse, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QASM syntax; unchecked: eigenphase_relation, semantic_correctness_of_circuit_vs_claim |
| qft_then_inverse_qft_identity_up_to_ordering | algorithms | algorithm_identity | intermediate | reference_claim | qasm_parse, lean_proof... | passing | proof_scope: full; headline: checked; checked_under: qspecbench.openqasm3.int_scaffold.v0, finite_matrix_model; not_checked: full_openqasm3, hardware_semantics; checked: Lean, QASM syntax, Python bridge; unchecked: semantic_correctness_of_circuit_vs_claim |
| superdense_coding_decodes_two_classical_bits | algorithms | protocol_correctness | introductory | reference_scaffold | qasm_parse, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QASM syntax; unchecked: decoding_relation, artifact_parsing_semantics, idealized_gate_semantics |
| swap_from_three_cx | algorithms | circuit_construction | introductory | reference_claim | qasm_parse, qasm_parse... | passing | proof_scope: full; headline: checked; checked_under: qspecbench.openqasm3.int_scaffold.v0, finite_matrix_model; not_checked: full_openqasm3, hardware_semantics; checked: Lean, QASM syntax, Python bridge; unchecked: unitary_equivalence_beyond_declared_gate_subset |
| teleportation_preserves_state_up_to_pauli_correction | algorithms | protocol_correctness | introductory | reference_scaffold | qasm_parse, lean_proof... | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QASM syntax, Python bridge; unchecked: arbitrary_state_relational_transfer, measurement_conditioned_pauli_correction, arbitrary_state_relational_transfer_after_measur, +2 more |
| circuit_identity_after_layout | equivalence | unitary_equivalence | introductory | reference_scaffold | qasm_parse, qasm_parse... | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QASM syntax, Python bridge; unchecked: register_renaming_semantics_beyond_isomorphic_ma |
| clifford_simplification_preserves_unitary | equivalence | unitary_equivalence | advanced | reference_scaffold | qasm_parse, qasm_parse... | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QASM syntax, Python bridge; unchecked: semantic_correctness_of_circuit_vs_claim |
| cnot_self_inverse_cancellation | equivalence | unitary_equivalence | introductory | reference_claim | qasm_parse, qasm_parse... | passing | proof_scope: full; headline: checked; checked_under: qspecbench.openqasm3.int_scaffold.v0, finite_matrix_model; not_checked: full_openqasm3, hardware_semantics; checked: Lean, QASM syntax, Python bridge; unchecked: matrix_model_matches_qasm_semantics_for_all_inst, general_n_qubit_extension_of_cancellation_rule |
| hadamard_conjugates_x_to_z | equivalence | unitary_equivalence | intermediate | reference_claim | lean_proof, qasm_parse... | passing | proof_scope: full; headline: checked; checked_under: qspecbench.openqasm3.int_scaffold.v0, finite_matrix_model; not_checked: full_openqasm3, hardware_semantics; checked: Lean, QASM syntax, Python bridge; unchecked: openqasm_h_normalization_links_integer_model_to_ |
| phase_polynomial_equivalence_small_instance | equivalence | unitary_equivalence | intermediate | reference_scaffold | qasm_parse, qasm_parse... | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QASM syntax, Python bridge; unchecked: semantic_correctness_of_circuit_vs_claim |
| qft_inverse_qft_small_instance | equivalence | unitary_equivalence | intermediate | reference_claim | qasm_parse, qasm_parse... | passing | proof_scope: full; headline: checked; checked_under: qspecbench.openqasm3.int_scaffold.v0, finite_matrix_model; not_checked: full_openqasm3, general_n_qubit_qft; checked: Lean, QASM syntax, Python bridge; unchecked: openqasm_h_normalization_matches_lean_integer_mo |
| rx_gate_equivalence_small_instance | equivalence | unitary_equivalence | introductory | reference_scaffold | lean_proof, qasm_parse... | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QASM syntax, Python bridge; unchecked: openqasm_rx_parameter_semantics_beyond_pi_2_inst, global_phase_between_rx_and_h |
| single_qubit_gate_cancellation | equivalence | unitary_equivalence | introductory | reference_claim | lean_proof, qasm_parse... | passing | proof_scope: full; headline: checked; checked_under: qspecbench.openqasm3.int_scaffold.v0, finite_matrix_model; not_checked: full_openqasm3, hardware_semantics; checked: Lean, QASM syntax, Python bridge; unchecked: openqasm_h_normalization_factor_links_to_integer |
| source_optimized_qasm_equivalence_small_instance | equivalence | unitary_equivalence | intermediate | reference_scaffold | qasm_parse, qasm_parse... | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QASM syntax, Python bridge; unchecked: semantic_correctness_of_circuit_vs_claim |
| toffoli_decomposition_equivalence | equivalence | unitary_equivalence | intermediate | reference_scaffold | qasm_parse, qasm_parse... | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QASM syntax, Python bridge; unchecked: decomposition_circuit_phase_semantics_beyond_qce |
| bravyi_kitaev_small_instance | hamiltonian | mapping_sanity | intermediate | usable | simulation | passing | proof_scope: syntax_or_review; headline: unproved; checked: declared checks; unchecked: simulation_heuristic, formal_anticommutation_preservation |
| heisenberg_model_hermiticity_small_instance | hamiltonian | hermiticity | introductory | reference_scaffold | simulation, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean; unchecked: formal_proof_in_lean |
| jordan_wigner_preserves_anticommutation_small_instance | hamiltonian | hamiltonian_claim | intermediate | reference_scaffold | simulation, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean; unchecked: formal_proof_of_claim |
| pauli_decomposition_matches_source_hamiltonian_small_instance | hamiltonian | hamiltonian_claim | advanced | reference_scaffold | simulation, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean; unchecked: formal_proof_of_claim |
| resource_contract_for_small_hamiltonian_simulation | hamiltonian | hamiltonian_claim | intermediate | reference_scaffold | simulation, lean_proof | passing | proof_scope: syntax_or_review; headline: unproved; checked: Lean; unchecked: resource_contract, formal_proof_of_claim |
| single_trotter_step_declares_error_contract | hamiltonian | hamiltonian_claim | intermediate | reference_contract | lean_proof, human_review | passing | proof_scope: fragment; headline: partially_checked; checked: Lean; unchecked: fidelity_achievement, fidelity_bound_is_achieved_by_the_declared_step |
| small_fermionic_hamiltonian_is_hermitian | hamiltonian | hermiticity | introductory | reference_claim | simulation, lean_proof | passing | proof_scope: full; headline: checked; checked_under: qspecbench.pauli_hamiltonian_model.v0, finite_matrix_model; not_checked: fermionic_source_semantics, jordan_wigner_mapping; checked: Lean; unchecked: jw_mapping, mapping_from_fermionic_source_to_pauli_artifact |
| trotter_second_order_bound_contract | hamiltonian | error_bound_contract | intermediate | reference_contract | lean_proof, human_review | passing | proof_scope: fragment; headline: partially_checked; checked: Lean; unchecked: operator_norm_bound, trotter_error_proof |
| bb84_sifted_key_partial_claim | qec | protocol_claim | intermediate | usable | human_review | passing | proof_scope: fragment; headline: partially_checked; checked: declared checks; unchecked: eavesdropper_model, privacy_amplification |
| detector_model_sanity_check | qec | model_sanity | introductory | usable | simulation | passing | proof_scope: syntax_or_review; headline: unproved; checked: declared checks; unchecked: simulation_heuristic, hardware_calibration |
| distance_certificate_small_css_code | qec | qec_claim | intermediate | usable | qec_verifier_result, qec_verifier_result... | passing | proof_scope: fragment; headline: partially_checked; checked: QEC structure; unchecked: algebraic_commutation_proof, decoder_and_correction_claims |
| logical_state_preserved_up_to_pauli_frame | qec | qec_claim | advanced | reference_scaffold | qec_verifier_result, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QEC structure; unchecked: algebraic_commutation_proof, decoder_and_correction_claims |
| repeated_round_qec_temporal_specification | qec | qec_claim | intermediate | seed | qec_verifier_result, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QEC structure; unchecked: algebraic_commutation_proof, decoder_and_correction_claims |
| repetition_code_three_one_three | qec | qec_claim | introductory | reference_scaffold | qec_verifier_result, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QEC structure; unchecked: distance_proof, decoder_correctness |
| shor_code_stabilizer_commutation | qec | stabilizer_commutation | intermediate | reference_scaffold | qec_verifier_result, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QEC structure; unchecked: algebraic_commutation_proof_beyond_scaffold, correction_and_distance_claims |
| steane_code_stabilizer_commutation | qec | qec_claim | intermediate | reference_scaffold | qec_verifier_result, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QEC structure; unchecked: algebraic_commutation_proof, decoder_and_correction_claims |
| surface_code_distance_three_stabilizer_sanity | qec | qec_claim | intermediate | reference_scaffold | qec_verifier_result, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QEC structure; unchecked: algebraic_commutation_proof, decoder_and_correction_claims |
| surface_code_single_pauli_error_correction | qec | qec_claim | intermediate | reference_scaffold | qec_verifier_result, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QEC structure; unchecked: algebraic_commutation_proof, decoder_and_correction_claims |
| surface_code_single_round_syndrome_extraction | qec | qec_claim | intermediate | reference_scaffold | qec_verifier_result, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QEC structure; unchecked: algebraic_commutation_proof, decoder_and_correction_claims |
| three_qubit_bit_flip_code_corrects_one_x | qec | error_correction | intermediate | reference_scaffold | qec_verifier_result, qec_verifier_result... | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QEC structure; unchecked: syndrome_extraction_circuit_semantics, decoder_algorithm_beyond_lookup_tables, repeated_round_fault_tolerance |
| three_qubit_phase_flip_code_corrects_one_z | qec | error_correction | intermediate | reference_scaffold | qec_verifier_result, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QEC structure; unchecked: correction_restores_logical_state |

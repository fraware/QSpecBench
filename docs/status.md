# QSpecBench Dashboard

Auto-generated benchmark status overview.

Evidence headline note: most reference-scaffold benchmarks demonstrate the QSpecBench evidence format and trust-boundary discipline; a checked headline may appear on `experimental_closed` (machine closure) or, when gold is unfrozen, on `reference_claim` / ABRC packages with authentic independent review (live gold inventory is empty for v1).

## Versions

- **Schema:** 0.3
- **Tooling:** 0.2.0
- **Corpus:** 0.2.0
- **Release tag:** v0.2.3

## Summary

- **Total benchmarks:** 52
- **By track:** ai_formalization: 7, algorithms: 11, equivalence: 12, hamiltonian: 9, qec: 13
- **By maturity:** experimental_closed: 21, reference_contract: 1, reference_scaffold: 22, seed: 1, usable: 7
- **With any checked evidence:** 48
- **With headline claim checked (reference_claim or checked headline):** 21
- **With scaffold-only checked evidence:** 27
- **With unchecked headline assumptions:** 31
- **With partial (non-checked) evidence only:** 4
- **With no evidence:** 0
- **With AI draft evidence:** 7
- **With approximate specifications:** 3
- **QEC claims:** 13
- **QEC small-code certificate level (`qec_small_code_checked`):** 12
- **QEC external certificate level (`qec_external_certificate_checked`):** 1
- **With resource contracts:** 11
- **Manifest-checked theorem bindings:** 4
- **Python denotation consistency checks:** 2
- **Kernel-checked codegen-trace bridges:** 1
- **Kernel-checked artifact-semantics bridges (legacy label):** 9
- **Documented (not proved) bridges:** 4
- **Coq/Rocq/Isabelle second-assistant evidence:** excluded from default maturity counts. Default CI does not install or invoke `coqc`. Optional local or custom-job checks use `QSPECBENCH_COQ=1` (see `adapters/coq/README.md`). Smoke file `cnot_coq_smoke.v` is documented but not compiled in default CI.

### Passing evidence by trust level

- **checked:** 61
- **independently_checkable:** 13
- **externally_trusted:** 67
- **heuristic:** 30

### Reference-scaffold coverage by track

- **ai_formalization:** 1
- **algorithms:** 5
- **equivalence:** 4
- **hamiltonian:** 5
- **qec:** 8

## Benchmarks

| ID | Track | Claim type | Difficulty | Maturity | Evidence | CI | Trust summary |
|---|---|---|---|---|---|---|---|
| extract_teleportation_correctness_statement | ai_formalization | formalization_faithfulness | intermediate | experimental_closed | lean_proof, human_review | passing | proof_scope: full; headline: checked; checked_under: qspecbench.ai_formalization.gold_target.v1, qspecbench.teleportation.computational_basis_measure_correct.v0; +1 bases; not_checked: full_faithfulness_of_ai_draft_text_to_source_phr, general_state_teleportation_beyond_computational; checked: Lean; unchecked: full_faithfulness_of_ai_draft_text_to_source_phr, general_state_teleportation_beyond_computational |
| formalize_bit_flip_code_corrects_one_x | ai_formalization | formalization_faithfulness | intermediate | experimental_closed | lean_proof, human_review | passing | proof_scope: full; headline: checked; checked_under: qspecbench.ai_formalization.gold_target.v1, qspecbench.qec.bit_flip_lookup_decoder.single_x.v0; +1 bases; not_checked: full_faithfulness_of_ai_draft_text_to_source_phr, syndrome_extraction_circuit_semantics; checked: Lean; unchecked: full_faithfulness_of_ai_draft_text_to_source_phr |
| formalize_no_cloning_statement | ai_formalization | formalization_faithfulness | introductory | reference_scaffold | lean_proof, human_review | passing | proof_scope: fragment; headline: partially_checked; checked: Lean; unchecked: draft_faithfulness, full_faithfulness_of_ai_draft_text_to_source_phr |
| formalize_qec_distance_claim_statement | ai_formalization | formalization | intermediate | usable | lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean; unchecked: full_faithfulness_of_ai_draft_text_to_source_phr |
| formalize_small_hamiltonian_hermiticity_statement | ai_formalization | formalization_faithfulness | intermediate | experimental_closed | lean_proof, human_review | passing | proof_scope: full; headline: checked; checked_under: qspecbench.ai_formalization.gold_target.v1, qspecbench.hamiltonian.small_fermionic_hamiltonian_is_hermitian.v0; +1 bases; not_checked: full_faithfulness_of_ai_draft_text_to_source_phr, general_size_hamiltonian_hermiticity_beyond_declared_instance; checked: Lean; unchecked: full_faithfulness_of_ai_draft_text_to_source_phr |
| formalize_stabilizer_commutation_statement | ai_formalization | formalization_faithfulness | intermediate | experimental_closed | lean_proof, human_review | passing | proof_scope: full; headline: checked; checked_under: qspecbench.ai_formalization.gold_target.v1, qspecbench.qec.steane_z_chain_adjacent_commutation.v0; +1 bases; not_checked: full_faithfulness_of_ai_draft_text_to_source_phr, all_pairs_stabilizer_commutation_general_code; checked: Lean; unchecked: full_faithfulness_of_ai_draft_text_to_source_phr |
| formalize_teleportation_spec_statement | ai_formalization | formalization | intermediate | usable | lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean; unchecked: full_faithfulness_of_ai_draft_text_to_source_phr |
| amplitude_damping_channel_specification | algorithms | channel_specification | intermediate | usable | simulation | passing | proof_scope: syntax_or_review; headline: unproved; checked: declared checks; unchecked: simulation_heuristic, cptp_property_proof |
| bell_state_preparation | algorithms | state_preparation | introductory | experimental_closed | qasm_parse, lean_proof... | passing | proof_scope: full; headline: checked; checked_under: qspecbench.openqasm3.int_scaffold.v0, finite_matrix_model; +2 bases; not_checked: full_openqasm3, global_phase_of_phi_state; checked: Lean, QASM syntax |
| deutsch_jozsa_constant_balanced_distinction | algorithms | oracle_distinction | intermediate | reference_scaffold | qasm_parse, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QASM syntax; unchecked: oracle_distinction, dj_correctness_for_constant_vs_balanced |
| grover_single_iteration_amplitude_amplification | algorithms | amplitude_amplification | intermediate | reference_scaffold | qasm_parse, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked_under: qspecbench.openqasm3.int_scaffold.v0, finite_matrix_model; +1 bases; checked: Lean, QASM syntax; unchecked: amplitude_lift, semantic_correctness_of_circuit_vs_claim |
| no_cloning_negative_claim | algorithms | negative_claim | frontier | reference_scaffold | lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean; unchecked: full_universal_cloner_formalization_beyond_basis |
| phase_estimation_exact_eigenphase_small_instance | algorithms | eigenphase_estimation | frontier | reference_scaffold | qasm_parse, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QASM syntax; unchecked: eigenphase_relation, semantic_correctness_of_circuit_vs_claim |
| qft_then_inverse_qft_identity_up_to_ordering | algorithms | algorithm_identity | intermediate | experimental_closed | qasm_parse, lean_proof... | passing | proof_scope: full; headline: checked; checked_under: qspecbench.openqasm3.int_scaffold.v0, finite_matrix_model; not_checked: full_openqasm3, general_n_qubit_rule; checked: Lean, QASM syntax; unchecked: semantic_correctness_of_circuit_vs_claim |
| superdense_coding_decodes_two_classical_bits | algorithms | protocol_correctness | introductory | reference_scaffold | qasm_parse, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QASM syntax; unchecked: decoding_relation, artifact_parsing_semantics, idealized_gate_semantics |
| swap_from_three_cx | algorithms | circuit_construction | introductory | experimental_closed | qasm_parse, qasm_parse... | passing | proof_scope: full; headline: checked; checked_under: qspecbench.openqasm3.int_scaffold.v0, finite_matrix_model; +4 bases; not_checked: full_openqasm3, hardware_semantics; checked: Lean, QASM syntax |
| teleportation_dynamic_feedforward_protocol | algorithms | dynamic_protocol_denotation | advanced | experimental_closed | qasm_parse, lean_proof... | passing | proof_scope: full; headline: checked; checked_under: kernel_checked_dynamic_denotation, kernel_checked_dynamic_ast_semantics; +5 bases; not_checked: full_openqasm3_dynamic_circuit, hardware_semantics; checked: Lean, QASM syntax |
| teleportation_preserves_state_up_to_pauli_correction | algorithms | protocol_correctness | introductory | experimental_closed | qasm_parse, lean_proof... | passing | proof_scope: full; headline: checked; checked_under: kernel_checked_artifact_semantics, kernel_checked_codegen_trace; +19 bases; not_checked: full_openqasm3_dynamic_circuit, hardware_semantics; checked: Lean, QASM syntax |
| circuit_identity_after_layout | equivalence | unitary_equivalence | introductory | reference_scaffold | qasm_parse, qasm_parse... | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QASM syntax; unchecked: register_renaming_semantics_beyond_isomorphic_ma |
| clifford_simplification_preserves_unitary | equivalence | unitary_equivalence | advanced | experimental_closed | qasm_parse, qasm_parse... | passing | proof_scope: full; headline: checked; checked_under: qspecbench.openqasm3.complex_unitary.v1, denotateOps1C_normalized; +4 bases; not_checked: unnormalized_denotateOps1C_pair_equality, full_openqasm3; checked: Lean, QASM syntax |
| cnot_self_inverse_cancellation | equivalence | unitary_equivalence | introductory | experimental_closed | qasm_parse, qasm_parse... | passing | proof_scope: full; headline: checked; checked_under: qspecbench.openqasm3.int_scaffold.v0, finite_matrix_model; +2 bases; not_checked: full_openqasm3, general_n_qubit_rule; checked: Lean, QASM syntax |
| hadamard_conjugates_x_to_z | equivalence | unitary_equivalence | intermediate | experimental_closed | lean_proof, qasm_parse... | passing | proof_scope: full; headline: checked; checked_under: qspecbench.openqasm3.int_scaffold.v0, finite_matrix_model; +2 bases; not_checked: full_openqasm3, hardware_semantics; checked: Lean, QASM syntax |
| native_ccx_artifact_denotes_toffoli_unitary | equivalence | unitary_denotation | intermediate | experimental_closed | qasm_parse, lean_proof... | passing | proof_scope: full; headline: checked; checked_under: qspecbench.openqasm3.int_scaffold.v0, finite_matrix_model; +2 bases; not_checked: decomposition_target_equivalence, full_openqasm3; checked: Lean, QASM syntax |
| phase_polynomial_equivalence_small_instance | equivalence | unitary_equivalence | intermediate | reference_scaffold | qasm_parse, qasm_parse... | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QASM syntax; unchecked: semantic_correctness_of_circuit_vs_claim |
| qft_inverse_qft_small_instance | equivalence | unitary_equivalence | intermediate | experimental_closed | qasm_parse, qasm_parse... | passing | proof_scope: full; headline: checked; checked_under: qspecbench.openqasm3.int_scaffold.v0, finite_matrix_model; not_checked: full_openqasm3, general_n_qubit_qft; checked: Lean, QASM syntax; unchecked: openqasm_h_normalization_matches_lean_integer_mo |
| qiskit_optimize_1q_gates_hxx_identity | equivalence | unitary_equivalence | intermediate | experimental_closed | qasm_parse, qasm_parse... | passing | proof_scope: full; headline: checked; checked_under: openqasm_fragment, qiskit_optimize_1q_gates_instance; not_checked: general_qiskit_correctness, full_openqasm3; checked: Lean, QASM syntax |
| rx_gate_equivalence_small_instance | equivalence | unitary_equivalence | introductory | reference_scaffold | lean_proof, qasm_parse... | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QASM syntax; unchecked: openqasm_rx_parameter_semantics_beyond_pi_2_inst, global_phase_between_rx_and_h |
| single_qubit_gate_cancellation | equivalence | unitary_equivalence | introductory | experimental_closed | lean_proof, qasm_parse... | passing | proof_scope: full; headline: checked; checked_under: qspecbench.openqasm3.int_scaffold.v0, finite_matrix_model; +2 bases; not_checked: full_openqasm3, hardware_semantics; checked: Lean, QASM syntax |
| source_optimized_qasm_equivalence_small_instance | equivalence | unitary_equivalence | intermediate | reference_scaffold | qasm_parse, qasm_parse... | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QASM syntax; unchecked: semantic_correctness_of_circuit_vs_claim |
| toffoli_decomposition_equivalence | equivalence | unitary_equivalence | intermediate | experimental_closed | qasm_parse, qasm_parse... | passing | proof_scope: full; headline: checked; checked_under: qspecbench.openqasm3.clifford_t_normalized.v1, denotateOps3C_normalized; +5 bases; not_checked: unnormalized_denotateOps3C_pair_equality, default_python_qasm_matrix_legacy_kron_3qubit; checked: Lean, QASM syntax |
| bravyi_kitaev_small_instance | hamiltonian | mapping_sanity | intermediate | usable | simulation | passing | proof_scope: syntax_or_review; headline: unproved; checked: declared checks; unchecked: simulation_heuristic, formal_anticommutation_preservation |
| heisenberg_model_hermiticity_small_instance | hamiltonian | hermiticity | introductory | reference_scaffold | simulation, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean; unchecked: formal_proof_in_lean |
| jordan_wigner_preserves_anticommutation_small_instance | hamiltonian | hamiltonian_claim | intermediate | reference_scaffold | simulation, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean; unchecked: formal_proof_of_claim |
| pauli_decomposition_matches_source_hamiltonian_small_instance | hamiltonian | hamiltonian_claim | advanced | reference_scaffold | simulation, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean; unchecked: formal_proof_of_claim |
| resource_contract_for_small_hamiltonian_simulation | hamiltonian | hamiltonian_claim | intermediate | reference_scaffold | simulation, lean_proof | passing | proof_scope: syntax_or_review; headline: unproved; checked: Lean; unchecked: resource_contract, formal_proof_of_claim |
| single_trotter_step_declares_error_contract | hamiltonian | hamiltonian_claim | intermediate | experimental_closed | lean_proof, lean_proof... | passing | proof_scope: full; headline: checked; checked_under: multi_step_trotter_composition, haar_monte_carlo_integral; +20 bases; not_checked: fidelity_1e-6_at_artifact_step, hardware_semantics; checked: Lean |
| small_fermionic_hamiltonian_is_hermitian | hamiltonian | hermiticity | introductory | experimental_closed | simulation, lean_proof | passing | proof_scope: full; headline: checked; checked_under: qspecbench.pauli_hamiltonian_model.v0, finite_matrix_model; not_checked: fermionic_source_semantics, hardware_semantics; checked: Lean; unchecked: jw_mapping, mapping_from_fermionic_source_to_pauli_artifact |
| trotter_second_order_bound_contract | hamiltonian | error_bound_contract | intermediate | reference_contract | lean_proof, human_review | passing | proof_scope: fragment; headline: partially_checked; checked: Lean; unchecked: operator_norm_bound, trotter_error_proof |
| xz_product_formula_frobenius_majorant_at_pi4 | hamiltonian | hamiltonian_claim | advanced | experimental_closed | lean_proof | passing | proof_scope: full; headline: checked; checked_under: pauli_xz_c2, t_pi_over_4; +1 bases; not_checked: general_operator_norm_lie_trotter, arbitrary_hermitian_A_B; checked: Lean |
| bb84_sifted_key_partial_claim | qec | protocol_claim | intermediate | usable | human_review | passing | proof_scope: fragment; headline: partially_checked; checked: declared checks; unchecked: eavesdropper_model, privacy_amplification |
| detector_model_sanity_check | qec | model_sanity | introductory | usable | simulation | passing | proof_scope: syntax_or_review; headline: unproved; checked: declared checks; unchecked: simulation_heuristic, hardware_calibration |
| distance_certificate_small_css_code | qec | qec_claim | intermediate | usable | qec_verifier_result, qec_verifier_result... | passing | proof_scope: fragment; headline: partially_checked; checked: QEC structure; unchecked: algebraic_commutation_proof, decoder_and_correction_claims |
| logical_state_preserved_up_to_pauli_frame | qec | qec_claim | advanced | reference_scaffold | qec_verifier_result, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QEC structure; unchecked: algebraic_commutation_proof, decoder_and_correction_claims |
| repeated_round_qec_temporal_specification | qec | qec_claim | intermediate | seed | qec_verifier_result, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QEC structure; unchecked: algebraic_commutation_proof, decoder_and_correction_claims |
| repetition_code_three_one_three | qec | qec_claim | introductory | reference_scaffold | qec_verifier_result, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QEC structure; unchecked: distance_proof, decoder_correctness |
| shor_code_stabilizer_commutation | qec | stabilizer_commutation | intermediate | reference_scaffold | qec_verifier_result, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QEC structure; unchecked: algebraic_commutation_proof_beyond_scaffold, correction_and_distance_claims |
| steane_code_stabilizer_commutation | qec | qec_claim | intermediate | reference_scaffold | qec_verifier_result, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QEC structure; unchecked: algebraic_commutation_proof, decoder_and_correction_claims |
| surface_code_distance_three_stabilizer_sanity | qec | qec_claim | intermediate | reference_scaffold | qec_verifier_result, lean_proof... | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QEC structure; unchecked: algebraic_commutation_proof, decoder_and_correction_claims |
| surface_code_single_pauli_error_correction | qec | qec_claim | intermediate | reference_scaffold | qec_verifier_result, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QEC structure; unchecked: algebraic_commutation_proof, decoder_and_correction_claims |
| surface_code_single_round_syndrome_extraction | qec | qec_claim | intermediate | reference_scaffold | qec_verifier_result, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QEC structure; unchecked: algebraic_commutation_proof, decoder_and_correction_claims |
| three_qubit_bit_flip_code_corrects_one_x | qec | error_correction | intermediate | experimental_closed | qec_verifier_result, qec_verifier_result... | passing | proof_scope: full; headline: checked; checked_under: stabilizer_tableau, lookup_table_decoder; +32 bases; not_checked: syndrome_decoding_correctness, undeclared_correlated_channels_beyond_dual_syndrome_flip; checked: Lean, QEC structure |
| three_qubit_phase_flip_code_corrects_one_z | qec | error_correction | intermediate | reference_scaffold | qec_verifier_result, lean_proof | passing | proof_scope: fragment; headline: partially_checked; checked: Lean, QEC structure; unchecked: correction_restores_logical_state |

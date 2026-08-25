# Claim diff: three_qubit_bit_flip_code_corrects_one_x

<!-- scope_fingerprint: 6d3f769dab13055f686f4c897d7c684cf7a8357e179a8fbb37d6a09e29a2eb8c -->

**Maturity:** experimental_closed
**Headline status:** checked

## Informal claim (README/spec)
Under the declared single-X Pauli bit-flip error model, the standard lookup-table decoder corrects each single X error with logical preservation verified by Lean 4 kernel proof and brute-force validation.

## Declared headline (claim_scope)
Under the declared single-X Pauli bit-flip error model, the standard lookup-table decoder corrects each single X error with logical preservation verified by Lean 4 kernel proof and brute-force validation.

## Required obligations
- code_definition
- stabilizer_commutation
- syndrome_extraction_circuit_semantics
- lookup_table_decoder
- decoder_correctness
- correction_restores_logical_state

## Checked obligations
- [x] code_definition
- [x] stabilizer_commutation
- [x] syndrome_extraction_circuit_semantics
- [x] lookup_table_decoder
- [x] decoder_correctness
- [x] correction_restores_logical_state
- [x] syndrome_extraction_circuit_semantics
- [x] repeated_round_fault_tolerance
- [x] three_round_majority_fault_tolerance
- [x] five_round_majority_fault_tolerance
- [x] seven_round_majority_fault_tolerance
- [x] spacetime_mwpm_fragment_fault_tolerance
- [x] stim_compatible_dem_adapter
- [x] external_matching_agrees_on_fixture_graph
- [x] stim_invoked_dem_pymatching
- [x] spacetime_mwpm_3qubit_bitflip_R3
- [x] spacetime_mwpm_repetition_d5_R5
- [x] spacetime_mwpm_repetition_d7_R7
- [x] full_spacetime_mwpm

## Unproved / open obligations

## Gap
- None among declared required obligations.

# Claim diff: three_qubit_bit_flip_code_corrects_one_x

<!-- scope_fingerprint: ec744ebd96ddf39c5a687bf0e03dc7d153cbdc7919fb418ee981d2af8d5a3966 -->

**Maturity:** reference_claim
**Headline status:** checked

## Informal claim (README/spec)
Under the declared single-X Pauli bit-flip error model, the standard lookup-table decoder corrects each single X error with logical preservation verified by Lean 4 kernel proof and brute-force validation.

## Declared headline (claim_scope)
Under the declared single-X Pauli bit-flip error model, the standard lookup-table decoder corrects each single X error with logical preservation verified by Lean 4 kernel proof and brute-force validation.

## Required obligations
- stabilizer_commutation
- lookup_table_decoder
- decoder_correctness
- correction_restores_logical_state

## Checked obligations
- [x] stabilizer_commutation
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

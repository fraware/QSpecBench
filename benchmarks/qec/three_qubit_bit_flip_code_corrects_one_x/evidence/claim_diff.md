# Claim diff: three_qubit_bit_flip_code_corrects_one_x

<!-- scope_fingerprint: 8b297b267d8c22cf1f7970229dad32c3a75b52a2a0b04060f40fb0358a853409 -->

**Maturity:** reference_claim
**Headline status:** checked

## Informal claim (README/spec)
Under the declared single-X Pauli bit-flip error model, the standard lookup-table decoder corrects each single X error with logical preservation verified by Lean 4 kernel proof and brute-force validation.

## Declared headline (claim_scope)
The three-qubit bit-flip code corrects every declared single-X Pauli error via the standard lookup-table decoder, with decoder correctness kernel-checked in Lean and logical preservation checked by brute force.

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

## Unproved / open obligations
- [ ] syndrome_extraction_circuit_semantics
- [ ] repeated_round_fault_tolerance

## Gap
- None among declared required obligations.

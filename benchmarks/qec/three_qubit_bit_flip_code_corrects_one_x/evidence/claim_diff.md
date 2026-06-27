# Claim diff: three_qubit_bit_flip_code_corrects_one_x

<!-- scope_fingerprint: 51df4d837b355051db68e7aef5ba838411b341dbc5a4204985f607a089080f7d -->

**Maturity:** reference_claim
**Headline status:** checked

## Informal claim (README/spec)
Under the declared single-X Pauli bit-flip error model, the standard lookup-table decoder corrects each single X error with logical preservation verified by brute-force validation (decoder algorithm assumed, not generally proved).

## Declared headline (claim_scope)
The three-qubit bit-flip code corrects every declared single-X Pauli error via the standard lookup-table decoder, with logical preservation checked by brute force (general decoder proof not claimed).

## Required obligations
- stabilizer_commutation
- lookup_table_decoder
- correction_restores_logical_state

## Checked obligations
- [x] stabilizer_commutation
- [x] lookup_table_decoder
- [x] correction_restores_logical_state

## Unproved / open obligations
- [ ] syndrome_extraction_circuit_semantics
- [ ] decoder_algorithm_beyond_lookup_tables
- [ ] repeated_round_fault_tolerance

## Gap
- None among declared required obligations.

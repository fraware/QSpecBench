# Claim diff: three_qubit_bit_flip_code_corrects_one_x

<!-- scope_fingerprint: cea37330d0a10e70b8d367dd8c9554adac50f112909df2ccf6d650ff269f1eae -->

**Maturity:** reference_scaffold
**Headline status:** partially_checked

## Informal claim (README/spec)
Under the declared single-X Pauli bit-flip error model with lookup-table decoder assumed, syndrome/correction tables align and logical preservation passes brute-force validation for all single-X errors.

## Declared headline (claim_scope)
Under the declared single-X Pauli bit-flip error model with lookup-table decoder assumed, syndrome/correction tables align and logical preservation passes brute-force validation for all single-X errors.

## Required obligations
- stabilizer_commutation
- syndrome_decoding_correctness
- correction_restores_logical_state

## Checked obligations
- [x] stabilizer_commutation
- [x] syndrome_decoding_correctness
- [x] correction_restores_logical_state

## Unproved / open obligations
- [ ] syndrome_extraction_circuit_semantics
- [ ] decoder_algorithm_beyond_lookup_tables
- [ ] repeated_round_fault_tolerance

## Gap
- Headline not marked checked despite obligation coverage; review maturity label.

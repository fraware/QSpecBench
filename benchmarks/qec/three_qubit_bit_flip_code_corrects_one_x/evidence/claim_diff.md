# Claim diff: three_qubit_bit_flip_code_corrects_one_x

<!-- scope_fingerprint: a649ccad30e641cc24eb6062b7d2fb387130da6d845800bebe1870aceae24f07 -->

**Maturity:** reference_scaffold
**Headline status:** partially_checked

## Informal claim (README/spec)
The three-qubit bit-flip code corrects any single X error on physical qubits under the declared Pauli bit-flip error model.

## Declared headline (claim_scope)
The three-qubit bit-flip code corrects any single X error on physical qubits under the declared Pauli bit-flip error model.

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

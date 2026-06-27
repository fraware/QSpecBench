# Claim diff: three_qubit_bit_flip_code_corrects_one_x

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

## Unproved / open obligations
- [ ] syndrome_decoding_correctness
- [ ] correction_restores_logical_state
- [ ] correction_restores_logical_state_for_all_single
- [ ] syndrome_extraction_circuit_semantics
- [ ] decoder_correctness_assumed

## Gap (required but not checked)
- correction_restores_logical_state
- syndrome_decoding_correctness

## Conflict
- Obligations appear in both required and unproved lists.

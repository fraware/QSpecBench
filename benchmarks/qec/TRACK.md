# QEC Track

## Purpose

Quantum error correction claims: codes, syndromes, decoding, correction, distance, temporal rounds.

## Accepted claim types

Code definition, stabilizer commutation, syndrome extraction, decoder correctness, correction, logical preservation, distance certificates.

## Accepted artifacts

Stabilizer JSON (`artifacts/code.json`), error models, syndrome/correction tables, circuits.

## Accepted evidence

QEC JSON validator, formal proofs, simulation (heuristic), external QEC verifiers.

## Good first claims

- `three_qubit_bit_flip_code_corrects_one_x` (intermediate, usable)
- `shor_code_stabilizer_commutation` (intermediate, seed)

## Examples

| ID | Difficulty | Notes |
|----|------------|-------|
| three_qubit_bit_flip_code_corrects_one_x | intermediate | Full code + tables; decoder assumed |
| surface_code_single_pauli_error_correction | advanced | Surface-code pattern |
| repeated_round_qec_temporal_specification | advanced | Temporal specification |

## Known limitations

Decoder correctness is often **assumed** explicitly. Separate code definition from decoder proof obligations using `qec_status`.

# QEC Track

## Purpose

Quantum error correction claims: codes, syndromes, decoding, correction, distance, temporal rounds.

## Accepted claim types

Code definition, stabilizer commutation, syndrome extraction, decoder correctness, correction, logical preservation, distance certificates.

## Accepted artifacts

Stabilizer JSON (`artifacts/code.json`), error models, syndrome/correction tables, circuits.

## Accepted evidence

QEC JSON validator, formal proofs, simulation (heuristic), external QEC verifiers, SMT distance scaffolds.

## Good first claims

- `three_qubit_bit_flip_code_corrects_one_x` (intermediate, reference)
- `shor_code_stabilizer_commutation` (intermediate, usable)

## Examples

| ID | Difficulty | Maturity | Notes |
|----|------------|----------|-------|
| bb84_sifted_key_partial_claim | intermediate | usable | Auto-synced from spec.yaml |
| detector_model_sanity_check | introductory | usable | Auto-synced from spec.yaml |
| distance_certificate_small_css_code | intermediate | usable | Auto-synced from spec.yaml |
| logical_state_preserved_up_to_pauli_frame | advanced | reference_scaffold | Auto-synced from spec.yaml |
| repeated_round_qec_temporal_specification | intermediate | seed | Auto-synced from spec.yaml |
| repetition_code_three_one_three | introductory | reference_scaffold | Auto-synced from spec.yaml |
| shor_code_stabilizer_commutation | intermediate | reference_scaffold | Auto-synced from spec.yaml |
| steane_code_stabilizer_commutation | intermediate | reference_scaffold | Auto-synced from spec.yaml |
| surface_code_distance_three_stabilizer_sanity | intermediate | reference_scaffold | Auto-synced from spec.yaml |
| surface_code_single_pauli_error_correction | intermediate | reference_scaffold | Auto-synced from spec.yaml |
| surface_code_single_round_syndrome_extraction | intermediate | reference_scaffold | Auto-synced from spec.yaml |
| three_qubit_bit_flip_code_corrects_one_x | intermediate | reference_claim | Auto-synced from spec.yaml |
| three_qubit_phase_flip_code_corrects_one_z | intermediate | reference_scaffold | Auto-synced from spec.yaml |

## Known limitations

Decoder correctness is often **assumed** explicitly. Separate code definition from decoder proof obligations using `qec_status`.

## Reference promotion

See [docs/reference_benchmarks.md](../../docs/reference_benchmarks.md). Partial protocol claims (`bb84_sifted_key_partial_claim`) and simulation-only sanity checks (`detector_model_sanity_check`) remain **usable** by design.

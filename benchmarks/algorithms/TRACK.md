# Algorithms Track

## Purpose

Encode correctness claims for canonical quantum algorithms: protocols, oracles, amplification, and impossibility results.

## Accepted claim types

`protocol_correctness`, `oracle_distinction`, `amplitude_amplification`, `algorithm_identity`, `negative_claim`, `eigenphase_estimation`.

## Accepted artifacts

QASM circuits, protocol notes, channel specifications, oracle definitions.

## Accepted evidence

Lean 4 proofs, human review, QASM parse (syntax), simulation (heuristic only).

## Good first claims

- `teleportation_preserves_state_up_to_pauli_correction` (introductory, reference_scaffold)
- `bell_state_preparation` (introductory, artifact_bound_reference_claim)

## Examples

| ID | Difficulty | Maturity | Notes |
|----|------------|----------|-------|
| amplitude_damping_channel_specification | intermediate | usable | Auto-synced from spec.yaml |
| bell_state_preparation | introductory | artifact_bound_reference_claim | Auto-synced from spec.yaml |
| deutsch_jozsa_constant_balanced_distinction | intermediate | reference_scaffold | Auto-synced from spec.yaml |
| grover_single_iteration_amplitude_amplification | intermediate | reference_scaffold | Auto-synced from spec.yaml |
| no_cloning_negative_claim | frontier | reference_scaffold | Auto-synced from spec.yaml |
| phase_estimation_exact_eigenphase_small_instance | frontier | reference_scaffold | Auto-synced from spec.yaml |
| qft_then_inverse_qft_identity_up_to_ordering | intermediate | reference_claim | Auto-synced from spec.yaml |
| superdense_coding_decodes_two_classical_bits | introductory | reference_scaffold | Auto-synced from spec.yaml |
| swap_from_three_cx | introductory | artifact_bound_reference_claim | Auto-synced from spec.yaml |
| teleportation_preserves_state_up_to_pauli_correction | introductory | reference_scaffold | Auto-synced from spec.yaml |

## Known limitations

Most usable benchmarks lack kernel-checked proofs. Algorithm profile metadata appears in `specification.preconditions` until a dedicated schema field is justified.

## Reference promotion

See [docs/reference_benchmarks.md](../../docs/reference_benchmarks.md). `swap_from_three_cx` and `amplitude_damping_channel_specification` remain **usable**: the former needs a Lean bridge with correct CX direction semantics; the latter lacks a kernel-checked channel proof.

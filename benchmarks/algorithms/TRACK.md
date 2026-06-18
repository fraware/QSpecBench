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

- `teleportation_preserves_state_up_to_pauli_correction` (introductory, relational)
- `no_cloning_negative_claim` (introductory, negative)

## Examples

| ID | Difficulty | Notes |
|----|------------|-------|
| teleportation_preserves_state_up_to_pauli_correction | introductory | Relational protocol, usable |
| no_cloning_negative_claim | introductory | Negative claim, seed |
| phase_estimation_exact_eigenphase_small_instance | frontier | Small-instance exact phase |

## Known limitations

Most seed benchmarks lack kernel-checked proofs. Algorithm profile metadata appears in `specification.preconditions` until a dedicated schema field is justified.

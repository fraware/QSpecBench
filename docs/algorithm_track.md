# Algorithm track

## Purpose

Encode correctness claims for canonical quantum algorithms.

## Accepted claim types

Protocol correctness, oracle distinction, amplitude amplification, algorithm identity, negative claims.

## Accepted artifacts

QASM circuits, protocol descriptions, oracle specifications.

## Accepted evidence

Lean 4 proofs, human review, simulation (heuristic), QASM parse.

## Rules

Declare fixed-size vs parameterized, oracle assumptions, semantic object (state, unitary, channel, distribution), and qubit ordering.

## Examples

- `teleportation_preserves_state_up_to_pauli_correction` — relational protocol
- `no_cloning_negative_claim` — negative claim

## Limitations

Seed benchmarks may lack kernel proofs; maturity labels reflect this honestly.

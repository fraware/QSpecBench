# Flagship specification: arbitrary-input dynamic teleportation

Status: **machine-closed experimental package** (`experimental_closed`). Not independently reviewed. Not a gold/reference claim.

The completed instance is [`teleportation_dynamic_feedforward_protocol`](../benchmarks/algorithms/teleportation_dynamic_feedforward_protocol/) plus [`lean/QSpecBench/Research/DynamicTeleportation.lean`](../lean/QSpecBench/Research/DynamicTeleportation.lean).

## Proposition (this instance)

An arbitrary normalized pure qubit is recovered after the pinned dynamic teleportation artifact's measurement instrument and classically controlled Pauli correction. The on-disk measure/if AST is bound to the Lean Measurement/ClassicalReg denotation.

This is **not** a mixed-state density-operator / CPTP channel identity.

## Closed obligations

1. `dynamic_ast_fail_closed_mirror`
2. `dynamic_denotation_bridge_metadata`
3. `lean_dynamic_denotation_protocol`
4. `dynamic_denotation_bridge_verify`
5. `arbitrary_pure_state_instrument`

## Residual

Mixed-state channel equality, full OpenQASM 3 dynamics, and hardware/device fidelity remain out of scope. Independent review is absent.

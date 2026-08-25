# Teleport unitary-prefix QASM denotes Generated codegen ops

## Claim

Under the Lean 4 kernel OpenQASM3 denotation, the measure-free artifact teleport-unitary-prefix.qasm parses to Generated.TeleportationUnitaryPrefix.ops and matches the declared unitary-prefix gate list (bridge-teleport-unitary-prefix-codegen).

## Why this matters

Machine-closed kernel binding for the measure-free teleport unitary prefix (Path B narrowing).
Formerly labeled ABRC as of v0.2.x; **demoted for v1** to `experimental_closed` (not gold /
independently reviewed). Full dynamic OpenQASM measure+if feed-forward remains out of
headline scope.

## Objects

- `artifacts/teleport_unitary_prefix.qasm` — measure-free H/CX prefix (headline source)
- `artifacts/teleportation.qasm` — full protocol reference (out of headline scope)

## Specification

Exact gate-list denotation under Lean OpenQASM3 kernel bridge.

## Evidence

- Lean kernel bridge + BridgeMetadata/elaborator pins
- verify-bridge kernel_checked_artifact_semantics
- Dual hash-bound formal/domain reviews for proposition v2 (retained as unauthenticated legacy; not v1 gold)

## Trust boundary

**Checked under:** kernel_checked_artifact_semantics on unitary-prefix artifact.

**Not checked under:** full_openqasm_dynamic_circuit_protocol; POVM/relational recovery as headline.

## Status

Current maturity: **experimental_closed**.

## Known gaps

Full dynamic teleport protocol with gold/ABRC promotion remains future work after the freeze
(measure+if outside gate-only chain; sibling package is also `experimental_closed`).

## References

- Nielsen and Chuang teleportation presentation

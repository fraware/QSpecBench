# Teleport unitary-prefix QASM denotes Generated codegen ops

## Claim

Under the Lean 4 kernel OpenQASM3 denotation, the measure-free artifact teleport-unitary-prefix.qasm parses to Generated.TeleportationUnitaryPrefix.ops and matches the declared unitary-prefix gate list (bridge-teleport-unitary-prefix-codegen).

## Why this matters

Artifact-bound kernel ABRC for the measure-free teleport unitary prefix (Path B narrowing).
Full dynamic OpenQASM measure+if feed-forward remains out of ABRC headline scope.

## Objects

- `artifacts/teleport_unitary_prefix.qasm` — measure-free H/CX prefix (ABRC source)
- `artifacts/teleportation.qasm` — full protocol reference (non-ABRC)

## Specification

Exact gate-list denotation under Lean OpenQASM3 kernel bridge.

## Evidence

- Lean kernel bridge + BridgeMetadata/elaborator pins
- verify-bridge kernel_checked_artifact_semantics
- Dual hash-bound formal/domain reviews for proposition v2

## Trust boundary

**Checked under:** kernel_checked_artifact_semantics on unitary-prefix artifact.

**Not checked under:** full_openqasm_dynamic_circuit_protocol; POVM/relational recovery as headline.

## Status

Current maturity: **artifact_bound_reference_claim**.

## Known gaps

Full dynamic teleport protocol ABRC remains future work (measure+if outside gate-only chain).

## References

- Nielsen and Chuang teleportation presentation

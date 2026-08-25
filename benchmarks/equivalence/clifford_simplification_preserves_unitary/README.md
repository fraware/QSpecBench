# Clifford simplification preserves unitary

## Claim

Clifford simplification of the declared H-H-S source trace to the S-only target circuit
preserves the unitary exactly under the normalized 1-qubit complex denotation (algebraic
H = H/√2; global phase φ = 0).

## Why this matters

Compiler equivalence representative for Clifford circuits; mirrors the honest machine-closure
path used by `toffoli_decomposition_equivalence` (normalized kernel-checked source/target
pair, elaborator-bound theorem, BridgeMetadata pin). Formerly ABRC as of v0.2.x; demoted for
v1 — not gold / independently reviewed.

## Objects

- `artifacts/source.qasm` — H H S (pre-simplification)
- `artifacts/target.qasm` — S (post-simplification)

## Specification

Exact matrix equality under `denotateOps1C_normalized` (trusted composition semantics for
this claim). Gate atoms H/S match `ComplexGate` normalized Hadamard / algebraic S matrices.

## Evidence

- QASM syntax checks (passing)
- QCEC on source/target pair (supporting external)
- Lean pair bridge: `evidence/clifford_pair_bridge.lean`
- verify-bridge: `evidence/bridge_verify.result.json`
- Policy: `notes/normalized_unitary_policy.md`, `notes/compiler_equivalence_gap.md`

## Trust boundary / checker chain

Checked obligations:

- `source_artifact_parse`
- `target_artifact_parse`
- `source_denotation`
- `target_denotation`
- `source_target_equivalence`
- `global_phase_policy`
- `wire_order_alignment`

Not claimed: unnormalized `denotateOps1C` pair equality (factor 2); full OpenQASM 3 /
hardware semantics.

## Status

Current maturity: **experimental_closed** (`kernel_checked_artifact_semantics`).

## Known gaps

- Unnormalized `denotateOps1C` exact source = target (intentionally out of scope; scaled
  by factor 2, see `notes/normalized_unitary_policy.md`)
- Full OpenQASM 3 / hardware semantics

## References

See `notes/normalized_unitary_policy.md`, `notes/compiler_equivalence_gap.md`, and sibling
`toffoli_decomposition_equivalence` for the reference promotion pattern.

## Claim diff

See evidence/claim_diff.md for declared vs checked obligation gap (Section C).

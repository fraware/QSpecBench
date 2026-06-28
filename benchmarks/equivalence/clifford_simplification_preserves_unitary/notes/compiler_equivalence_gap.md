# Compiler equivalence gap (Clifford simplification)

## What is checked

- **Source trace**: manifest `bridge_clifford_hhs` on `artifacts/source.qasm` (H H S).
- **QCEC**: external equivalence check on source vs target QASM pair.
- **verify-bridge**: Python matrix extractor matches Lean complex denotation on the
  **source** gate trace only.

## Source vs target manifest (Phase 4)

`bridge_theorem_manifest.json` now records **target-side** hashes for this benchmark:

- `target_qasm_artifact`, `target_artifact_sha256`, `target_gate_trace_sha256`
- `target_lean_theorem`: `bridge_clifford_s_single` on single-S trace
- `target_ast_sha256`, `target_generated_lean_sha256` (codegen stub)

`qspecbench bridge-codegen verify` checks both source and target codegen hashes when present.

## Open kernel proof (source→target)

`evidence/source_target_equivalence_open.lean` documents the missing Lean theorem relating
`denotateOps1C clifford_hhs` to `denotateOps1C clifford_s_single`. QCEC certifies pair
equivalence externally; QSpecBench does **not** claim `kernel_checked_artifact_semantics`
for the compiler pass.

## Honest scope

Headline claim ("simplification preserves unitary") remains `partially_checked`:
compiler pass correctness is evidenced by QCEC + source anchor, not a dual-manifest
hash chain for both artifacts.

## Toffoli / circuit_identity (Phase 8 evaluation)

`toffoli_decomposition_equivalence` and `circuit_identity_after_layout` remain
`manifest_checked_theorem_binding` only: manifest entries have `ast_sha256: null` and
no codegen kernel theorem wired. CCX / layout-identity denotation chains are higher-risk
than the five promoted kernel bridges; defer until CCX codegen stubs and proofs land.

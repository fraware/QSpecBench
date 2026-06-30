# Codegen blockers (Toffoli decomposition)

## What is checked today

- **Source CCX trace**: kernel-checked `bridge_toffoli_codegen_ccx` on `artifacts/source.qasm`.
- **QCEC**: external equivalence on source vs `artifacts/target.qasm` (H/T/CX decomposition).
- **Target codegen hashes** (Phase 4): manifest records `target_ast_sha256` and
  `target_generated_lean_sha256` for the decomposition circuit; verified by
  `qspecbench bridge-codegen verify` without a kernel source→target theorem.

## Open blockers (not `kernel_checked_artifact_semantics`)

1. **No Lean parse theorem on target artifact** — target-side ops are hash-pinned only.
2. **No kernel equivalence theorem** — CCX denotation equals decomposition trace in Lean.
3. **Wire-order / phase** — T/Tdg phase gates use complex diagonal model; global phase
   policy matches QCEC external check, not a closed Lean chain.

## Honest scope

Headline claim remains `reference_scaffold`: QCEC + source kernel bridge; target manifest
anchors document the decomposition gate list for future promotion work.

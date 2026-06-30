# Codegen blockers (Toffoli decomposition)

## What is checked today

- **Source CCX trace**: kernel-checked `bridge_toffoli_codegen_ccx` and `bridge_toffoli_codegen_ccxC`.
- **QCEC**: external equivalence on source vs `artifacts/target.qasm` (H/T/CX decomposition).
- **Target codegen**: parse theorem `parseQasmSource_toffoli_target_kernel_eq_generated_ops`;
  `denotateOps3C` scaffold on target trace.

## Open blockers (not `kernel_checked_artifact_semantics`)

1. **No pair kernel theorem** — `denotateOps3C` CCX source = decomposition target (exact or global phase).
2. **Unnormalized model mismatch** — Python `qasm_matrix` source/target matrices differ structurally.
3. **Global phase** — QCEC physical semantics not closed in Lean.

## Honest scope

Headline claim remains **artifact_bound_reference_claim** (source CCX only); QCEC pair check is supplementary. See
`notes/pair_equivalence_policy.md` and `evidence/source_target_pair_open.lean`.

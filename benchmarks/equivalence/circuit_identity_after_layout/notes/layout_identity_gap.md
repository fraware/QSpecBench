# Layout identity gap (C3)

## Blocker

`circuit_identity_after_layout` remains `manifest_checked_theorem_binding`. There is no closed chain:

```
layout-mapped QASM bytes → parseQasmSource → codegen ops → kernel layout theorem
```

## What exists

- Lean scaffold `layout_identity_ops` and `bridge_circuit_identity_after_layout` on a fixed H+CX trace.
- verify-bridge matrix consistency on declared artifacts.

## Missing for kernel_checked_artifact_semantics

- Register renaming / layout permutation semantics in canonical AST.
- Dual-artifact codegen hashes (pre-layout vs post-layout) with kernel equivalence proof.
- Wire-order bridge for permuted qubit indices beyond the 2-qubit CNOT special case.

## Honest label

Do not promote to `reference_claim` until layout permutation is manifest-bound and kernel-checked.

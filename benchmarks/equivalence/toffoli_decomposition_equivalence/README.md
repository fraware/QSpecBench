# Toffoli decomposition equivalence

## Claim

Native CCX on the declared three-qubit **source** QASM artifact denotes the standard Toffoli unitary under kernel-checked artifact semantics.

## Why this matters

Compiler decomposition track; source-side CCX artifact binding is the kernel-checked anchor before full source→target equivalence.

## Objects

- `artifacts/source.qasm` — native CCX (SHA256-bound; LF bytes)
- `artifacts/target.qasm` — H/T/CX decomposition (supplementary; QCEC only)

## Specification

Source artifact CCX denotation checked under int-scaffold / complex unitary model. Decomposition pair equivalence is **not** part of the artifact_bound headline.

## Evidence

- QASM syntax checks (passing; syntax only)
- **Lean 4 kernel proof** `QSpecBench.Quantum.OpenQASM3.bridge_toffoli_codegen_ccx` (passing)
- **Artifact parse chain**: `parseQasmSourceToOps toffoliKernelArtifactSource = some Generated.ToffoliDecompositionEquivalence.ops`
- QCEC on source/target pair (supplementary; not headline obligation)
- Pair scaffold: `evidence/source_target_pair_open.lean` + `notes/pair_equivalence_policy.md`
  (`pair_lean_theorem`: scoped C2 bridge, not full denotation equality)
- `qspecbench bridge-codegen verify` + `qspecbench bridge-metadata verify` (CI)

## Trust boundary / checker chain

| Stage | Anchor | Checked by |
|-------|--------|------------|
| Source QASM bytes | `artifact_sha256` | provenance + Lean `toffoliKernelArtifactSource` |
| Canonical AST | `lean_ast_sha256` (`ast_authority: lean_mirror`) | Lean-mirror parse on source |
| Generated ops | `generated_lean_sha256` | lake build + manifest |
| Kernel claim | `theorem_elaborator_hash` (primary) | BridgeMetadata pins |

Honest limits: source CCX artifact only; decomposition target trace hashed but pair equivalence not claimed at this tier.

## Status

Current maturity: **artifact_bound_reference_claim** (source-side `kernel_checked_artifact_semantics`).

## Known gaps

- Kernel-checked `denotateOps3C` source CCX = target decomposition (exact or global phase); scoped
  pair bridge pins source CCX + target parse only (`pair_equivalence_policy.md`)
- Decomposition circuit phase semantics beyond QCEC
- Full OpenQASM 3 / hardware semantics

## References

- Standard Toffoli / CCX gate semantics

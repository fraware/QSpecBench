# Hadamard conjugates X to Z

## Claim

Conjugating Pauli X by H yields Pauli Z up to global phase on one qubit.

## Why this matters

Pauli conjugation equivalence used throughout Clifford reasoning.

## Objects

- `artifacts/source.qasm` — H X H circuit (SHA256-bound; LF bytes)
- `artifacts/target.qasm` — Z gate

## Specification

Exact equivalence up to global phase on one qubit under the int-scaffold model.

## Evidence

- QASM syntax checks (passing; syntax only)
- **Lean 4 kernel proof** `QSpecBench.Quantum.OpenQASM3.bridge_hadamard_codegen_conjugates_x` (passing)
- **Artifact parse chain**: `parseQasmSourceToOps hxhKernelArtifactSource = some Generated.HadamardConjugatesXToZ.ops`
- QCEC external equivalence (supplementary)
- `qspecbench bridge-codegen verify` + `qspecbench bridge-metadata verify` (CI)

## Trust boundary / checker chain

| Stage | Anchor | Checked by |
|-------|--------|------------|
| QASM bytes | `artifact_sha256` | provenance + Lean embedded source |
| Canonical AST | `lean_ast_sha256` (`ast_authority: lean_mirror`) | Lean-mirror parse |
| Generated ops | `generated_lean_sha256` | lake build + manifest |
| Kernel claim | `theorem_elaborator_hash` (primary) | BridgeMetadata pins |

Honest limits: int-scaffold only; OpenQASM H normalization not checked under this headline.

## Status

Current maturity: **artifact_bound_reference_claim** (`kernel_checked_artifact_semantics`).

## Known gaps

- OpenQASM H normalization links integer model to gate semantics
- Full OpenQASM 3 / hardware semantics

## References

- Standard Pauli conjugation by Hadamard

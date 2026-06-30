# Bell state preparation

## Claim

Hadamard on q[0] followed by CNOT prepares the Bell state |Phi+> on two qubits.

## Why this matters

Foundational entanglement circuit for protocol benchmarks.

## Objects

- `artifacts/circuit.qasm` — H then CX (SHA256-bound; LF bytes)

## Specification

Exact state-preparation claim on |00> input under the int-scaffold model.

## Evidence

- QASM syntax checks (passing; syntax only)
- **Lean 4 kernel proof** `QSpecBench.Quantum.OpenQASM3.bridge_bell_codegen_prep` (passing)
- **Artifact parse chain**: `parseQasmSourceToOps bellKernelArtifactSource = some Generated.BellStatePreparation.ops`
- `qspecbench bridge-codegen verify` + `qspecbench bridge-metadata verify` (CI)

## Trust boundary / checker chain

| Stage | Anchor | Checked by |
|-------|--------|------------|
| QASM bytes | `artifact_sha256` | provenance + Lean embedded source |
| Canonical AST | `lean_ast_sha256` (`ast_authority: lean_mirror`) | Lean-mirror parse |
| Generated ops | `generated_lean_sha256` | lake build + manifest |
| Kernel claim | `theorem_elaborator_hash` (primary) | BridgeMetadata pins |

Honest limits: int-scaffold Bell prep; global phase and OpenQASM H normalization not checked under this headline.

## Status

Current maturity: **artifact_bound_reference_claim** (`kernel_checked_artifact_semantics`).

## Known gaps

- OpenQASM H normalization links integer model to gate semantics
- Global phase of |Phi+> state
- Full OpenQASM 3 / hardware semantics

## References

- Standard Bell state preparation circuit

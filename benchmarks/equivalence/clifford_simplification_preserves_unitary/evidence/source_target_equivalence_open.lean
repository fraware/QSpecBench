/- QSpecBench evidence: open source→target denotation equivalence (not kernel-checked).

benchmark_id = "clifford_simplification_preserves_unitary"
obligation_id = "compiler_source_target_denotation"
status = "open"

Source trace: H H S on q[0] (`bridge_clifford_hhs`, manifest-bound).
Target trace: S on q[0] (`bridge_clifford_s_single`, manifest-bound + target codegen hashes).

A kernel-checked compiler equivalence would require a Lean theorem relating
`denotateOps1C clifford_hhs` to `denotateOps1C clifford_s_single` (global phase policy
declared). QCEC certifies the pair externally; this file records the proof gap only.

## Next proof obligation checklist

1. [ ] Declare global-phase policy for complex denotation (`denotateOps1C`).
2. [ ] Prove `denotateOps1C clifford_hhs` equals `denotateOps1C clifford_s_single` up to phase.
3. [ ] Wire dual-manifest `kernel_checked_artifact_semantics` (source + target codegen hashes).
4. [~] Add Python cross-test: source/target AST gate lines vs `OpenQASM3Parser.parseLines` (H/X/CX subset; Phase 8 covers kernel bridges only).
5. [ ] Dual review before any `reference_claim` promotion on compiler equivalence.
-/

import QSpecBench.Quantum.OpenQASM3

#check QSpecBench.Quantum.OpenQASM3.bridge_clifford_hhs
#check QSpecBench.Quantum.OpenQASM3.bridge_clifford_s_single

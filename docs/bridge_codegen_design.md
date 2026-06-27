# OpenQASM-to-Lean bridge codegen design (deferred)

Full **kernel-checked artifact semantics** (`kernel_checked_artifact_semantics`) requires Lean proofs
that the OpenQASM artifact denotes the same operator as the formal gate semantics — not merely a
manifest-listed theorem on a fixed gate trace.

## Current state

- **manifest_checked_theorem_binding**: allowlisted gate trace + Lean theorem name + SHA256 hashes
- **python_denotation_consistency**: Python matrix extractor matches Lean `denotateOps*` on trace
- **RX blocker**: `ComplexGate.rxGate` exists, but `OpenQASM3` still uses H-plumbing for RX traces

## Target architecture

```mermaid
flowchart LR
  QASM["artifacts/*.qasm"] --> AST["QASM AST + ast_sha256"]
  AST --> Trace["Normalized gate trace"]
  Trace --> LeanGen["Generated Lean snippet"]
  LeanGen --> Proof["Kernel proof: trace denotation = artifact matrix"]
  Proof --> Bridge["semantic_bridge.claimed_link = kernel_checked_artifact_semantics"]
```

## Planned steps

1. **AST canonicalization** — stable JSON AST, `ast_sha256` in `bridge_theorem_manifest.json`
2. **Codegen** — emit Lean `def <benchmark>_ops` from trace (parameterized gates: RX(θ), RZ(θ), U)
3. **Proof templates** — `denotateOpsN <benchmark>_ops = <matrix>` by `fin_cases` or tactic macro
4. **Hash pipeline** — `generated_lean_sha256`, CI drift check vs manifest
5. **Obligation wiring** — `obligation_ids` in manifest maps theorems to `claim_scope` entries
6. **First candidate** — `cnot_self_inverse_cancellation` (already proved manually) retrofitted as codegen golden test
7. **Second candidate** — parameterized RX(π/2) using `ComplexGate.rxGate`, replacing H scaffold

## Out of scope for first kernel bridge

- Dynamic circuits (measurement, classical control)
- Full OpenQASM3 language
- Hardware calibration semantics

## RX(θ) blocker (rx_gate_equivalence_small_instance)

`ComplexGate.rxGate (θ : ℝ)` exists with θ = π/2 matching the Python unnormalized-H bridge matrix.
`OpenQASM3.QasmOp` has no parameterized `rx` constructor yet; `rx_parser_plumbing_ops` uses `.H`
as a stand-in for parser plumbing only. Promoting `rx_gate_equivalence_small_instance` to
`manifest_checked_theorem_binding` requires:

1. Add `QasmOp.rx (θ : ℝ) (q : Nat)` (or fixed π/2 variant) to the Lean trace type
2. Wire `denotateOps*` through `ComplexGate.rxGate`
3. Regenerate manifest entry with real gate trace + hashes

Until then, the benchmark stays `reference_scaffold` with `python_denotation_consistency` only.

## CI implications

- New job: `bridge-codegen verify` comparing manifest hashes to generated Lean
- Keeps separate from manifest binding job to avoid conflating trust levels

See [roadmap.md](roadmap.md) P1/P2 milestones.

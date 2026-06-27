# Evidence model

Evidence supports a claim; only **checked** evidence with a declared checker can support a "proved" reading.

## Proof assistant policy

**Lean 4 is the currently supported proof assistant in CI.** Stub adapters exist for Coq, Rocq, and Isabelle (`coq_proof`, `rocq_proof`, `isabelle_proof`); they return `not_checked` until a kernel is configured. The evidence taxonomy is proof-assistant-neutral.

## Evidence types (schema enum)

| Type | Role | Typical trust |
|------|------|---------------|
| `lean_proof` | Lean 4 proof | `checked` |
| `smt_certificate` | SMT certificate | `checked` / `independently_checkable` |
| `sat_certificate` | SAT / small-instance certificate | `independently_checkable` |
| `qcec_result` | Circuit equivalence tool | `externally_trusted` |
| `qbricks_result` | QBricks output | `externally_trusted` |
| `qec_verifier_result` | QEC verifier / JSON validator | `externally_trusted` |
| `zx_certificate` | ZX rewrite certificate | `externally_trusted` |
| `qasm_parse` | Syntax parse only | `externally_trusted` (syntax) |
| `simulation` | Numeric / sampling | `heuristic` |
| `human_review` | Expert review | `externally_trusted` |
| `ai_draft` | LLM-generated formalization | `untrusted` |
| `other` | Extension point | declare honestly |

## Checked evidence (Lean 4)

QSpecBench uses **Lean 4** for kernel-checked proofs in CI.

```
lean/
  lakefile.lean
  lean-toolchain
  QSpecBench/          -- proof modules
benchmarks/.../evidence/*.lean   -- evidence anchors
```

CI installs elan, runs `lake build`, then `qspecbench check-evidence`. Proofs containing `sorry` cannot pass.

Example reference: `cnot_self_inverse_cancellation` with `lean_proof` evidence.

## Tool-checked evidence

Specialized tools (QCEC, QEC JSON validator, QASM parser). **QASM parse is syntax only.**

## Heuristic evidence

Simulation and numeric scripts — **not proof**.

## AI-generated evidence

Always `untrusted` until independently checked and semantically reviewed.

## Status values

| Status | Meaning |
|--------|---------|
| `passing` | Checker succeeded |
| `failing` | Checker failed |
| `partial` | Incomplete support |
| `not_checked` | Not run |
| `draft` | Untrusted draft |

```bash
qspecbench check-evidence benchmarks/<track>/<claim_id>/
qspecbench check-evidence benchmarks/
```

# Reference benchmark governance (Layer 3)

Reference benchmarks are gold-standard exemplars with reproducible checked evidence. Promotion requires meeting track-specific stacks below.

## Universal requirements

- `status.maturity: reference` and `status.ci: passing`
- At least one passing evidence entry with `trust_level: checked` (`lean_proof`, `sat_certificate`, or `smt_certificate`)
- Complete `trust_boundary` with honest `assumptions_not_checked`
- README claim card documents scope limits (decoder assumed, global phase, etc.)

## QASM + Lean equivalence claims

- `expected/semantic_bridge.json` declaring `artifact_gate_model`, `lean_module`, `lean_theorem`, `normalization`
- Passing `bridge_verify` evidence when `claimed_link: kernel_checked`
- OpenQASM artifact parses and matrix matches `QSpecBench.Quantum.OpenQASM3` denotation

## Track stacks

| Track | Reference exemplar stack |
|-------|--------------------------|
| equivalence | Lean kernel proof + semantic bridge + (QCEC or SAT cert on small instance) |
| algorithms | Lean relational/unitary proof on fixed instance OR simulation + human review with documented oracle |
| qec | Stabilizer JSON validation + Lean commutation (decoder/correction may remain assumed) |
| hamiltonian | Lean `Hermitian` or matrix equality on declared Pauli model |
| ai_formalization | Kernel-checked draft + semantic rubric score >= 4 + named reviewer role |

## Anti-patterns (do not promote)

- Simulation-only evidence labeled as checked proof
- `correction_claim: checked` without checked decoder evidence
- `claimed_link: kernel_checked` without passing verify-bridge
- AI draft passing without independent kernel check and human review

## Promotion workflow

1. Open a reference promotion proposal (issue template)
2. Add evidence until the track stack is satisfied
3. Run `qspecbench validate`, `qspecbench check-evidence`, `lake build`
4. Maintainer review of `trust_boundary` honesty

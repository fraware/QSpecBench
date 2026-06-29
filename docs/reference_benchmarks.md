# Reference benchmark governance (Layer 3)

Reference levels are **scoped**. A benchmark may have reproducible checked evidence for *part* of its
claim (`reference_scaffold`, `reference_contract`, `reference_artifact`) while the full informal
headline claim is still unproved. The headline claim is only considered proved at `reference_claim`.

## Scoped reference levels

| Level | Meaning |
|-------|---------|
| `reference_scaffold` | Passing CI + at least one checked-evidence obligation; headline only partially checked. |
| `reference_contract` | Same, where the checked evidence is a declared contract (resource/error bound) rather than a proof of the bound. |
| `reference_artifact` | Same, where the checked evidence is artifact-structural (e.g. stabilizer commutation). |
| `reference_claim` | Headline claim fully proved (see requirements below). |
| `artifact_bound_reference_claim` | **Reserved (schema v0.2):** headline checked and explicitly bound to named artifact SHA256 anchors plus checker chain. Documented for future promotion; not assigned to any benchmark yet. |

## Universal requirements (any scoped reference level)

- `status.ci: passing`
- At least one passing evidence entry with `trust_level: checked` (`lean_proof`, `sat_certificate`, or `smt_certificate`)
- Complete `trust_boundary` with honest `assumptions_not_checked`
- README claim card documents scope limits (decoder assumed, global phase, etc.)
- Every `evidence.type` is declared in `acceptable_evidence`

## Additional requirements for `reference_claim`

- `claim_scope` (headline_claim_id, headline_claim_text, required_obligations) is declared
- `proved_scope.checked_obligations` covers every required obligation; none remain in `unproved_obligations`
- `headline_claim_status.status: checked`
- `headline_claim_status.checked_under` lists semantic bases (e.g. `qspecbench.openqasm3.int_scaffold.v0`, `finite_matrix_model`)
- `headline_claim_status.not_checked_under` lists explicit limits (e.g. `full_openqasm3`, `hardware_semantics`)
- Every `acceptable_evidence` entry with `required_for_claim: true` has a passing evidence entry of that type

## QASM + Lean equivalence claims

- `expected/semantic_bridge.json` declaring `artifact_gate_model`, `lean_module`, `lean_theorem`, `normalization`
- Passing `bridge_verify` evidence when `claimed_link` is `python_denotation_consistency` or `manifest_checked_theorem_binding`
- OpenQASM artifact parses and matrix matches `QSpecBench.Quantum.OpenQASM3` denotation (for Python bridge links)
- `python_denotation_consistency`: Python matrix vs denotation only
- `manifest_checked_theorem_binding`: manifest entry + SHA256 anchors + structured Lean evidence anchor (see `cnot_self_inverse_cancellation`)
- `kernel_checked_artifact_semantics`: five bridges with codegen AST + kernel proof + hash chain (see `cnot_self_inverse_cancellation`, `bell_state_preparation`, `swap_from_three_cx`)

## QEC claim scope (v0.2)

`qec_claim_scope` uses granular fields: `code_schema`, `code_definition_semantics`, `stabilizer_commutation`,
`syndrome_table`, `correction_table`, `decoder_algorithm`, `logical_preservation_small_code`,
`logical_preservation_general`, and `distance.status`. Mark `stabilizer_commutation: checked` only when
Lean evidence validates commutation. Mark `distance.status: checked` only with `distance_result` from
the QEC adapter bruteforce run.

## Track stacks

| Track | Scaffold exemplar stack |
|-------|--------------------------|
| equivalence | Lean kernel proof + semantic bridge + (QCEC or SAT cert on small instance) |
| algorithms | Lean relational/unitary proof on fixed instance OR simulation + human review with documented oracle |
| qec | Stabilizer JSON validation + Lean commutation (decoder/correction may remain assumed at scaffold level) |
| hamiltonian | Lean `Hermitian` or matrix equality on declared Pauli model |
| ai_formalization | Kernel-checked draft + semantic rubric score >= 4 + named reviewer role |

For a QEC `reference_claim`, the correction claim must be backed by checked correction evidence (not an
assumed lookup table); stabilizer commutation alone supports at most `reference_scaffold` /
`reference_artifact`.

## Anti-patterns (do not promote)

- Simulation-only evidence labeled as checked proof
- `reference_claim` while any required headline obligation is unproved
- `correction_claim: checked` without checked decoder/correction evidence
- `headline_claim_status: checked` on a scaffold-level benchmark
- `claimed_link: python_denotation_consistency` without passing verify-bridge
- Reporting manifest bindings or Python consistency as kernel-checked artifact semantics
- AI draft passing without independent kernel check and human review

## Promotion workflow

1. Open a reference promotion proposal (issue template)
2. Add evidence until the track stack is satisfied
3. Run `qspecbench validate`, `qspecbench check-evidence`, `lake build`
4. Maintainer review of `trust_boundary` honesty

## Current corpus (declared internal scope)

- **`reference_claim`:** 9 benchmarks (see dashboard)
- **`manifest_checked_theorem_binding` bridges:** 11
- **`python_denotation_consistency` bridges:** 2
- **`kernel_checked_artifact_semantics`:** 5

Regenerate counts: `qspecbench dashboard benchmarks/ --out docs/status.md`

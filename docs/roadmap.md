# Research and infrastructure roadmap

QSpecBench separates **infrastructure** (schema, validators, honest labels) from **scientific
results** (full protocol proofs). The dashboard counts each honestly.

## Infrastructure (tooling milestones)

- Wire all artifact JSON through schema validation in CI
- Expand `bridge_theorem_manifest.json` to every sound QASM+Lean pair
- Align Lean `ComplexGate` with Python for S/T/Rz or quarantine Clifford bridges
- QEC `single_pauli_error_correction_validator` + promotion path for small codes
- Release bundle CLI (`qspecbench release-bundle`)
- Second proof assistant in CI (Coq/Rocq/Isabelle beyond stubs)

## Research (corpus milestones — not validator tasks)

These require new mathematics or substantial formalization effort:

| Claim area | Example benchmark | What a real proof requires |
|------------|-------------------|----------------------------|
| Teleportation protocol | `teleportation_preserves_state_up_to_pauli_correction` | Measurement, classical feed-forward, arbitrary-state relational semantics |
| QEC correction | `three_qubit_bit_flip_code_corrects_one_x` | Decoder correctness + logical preservation, not lookup-table assumption |
| Algorithm correctness | Grover, Deutsch–Jozsa, phase estimation | Full algorithm specs, not scaffold nontriviality |
| No-cloning | `no_cloning_negative_claim` | Arbitrary states and linear maps, not permutation-matrix scaffold |
| Hamiltonian analytics | Trotter contracts | Analytic error bounds, not declared positive constants |
| Distance | `distance_certificate_small_css_code` | Actual minimum weight, not SMT toy `d ≥ 3` |

Promoting any of these to `reference_claim` before the proof exists would violate the project’s core
honesty rule.

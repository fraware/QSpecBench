# Research and infrastructure roadmap

QSpecBench separates **infrastructure** (schema, validators, honest labels) from **scientific
results** (full protocol proofs). The dashboard counts each honestly.

## Infrastructure (tooling milestones)

- [x] Wire artifact JSON through schema validation in `qspecbench validate` (B5)
- [x] Expand `bridge_theorem_manifest.json` to 9 sound QASM+Lean pairs without S/T (B1)
- [x] Align Lean `ComplexGate` with Python for S/T; kernel_checked Clifford and phase-polynomial bridges (B2)
- [x] QEC `single_pauli_error_correction_validator` brute-force logical preservation (B4)
- [x] OpenQASM `rz`/`ry`/`cz`/`u` in Python matrix extractor (B3)
- [x] Release bundle CLI stub (`qspecbench release-bundle`) (D)
- [ ] Second proof assistant in CI (Coq/Rocq/Isabelle beyond stubs)

### B1 bridge manifest (2026-06-27)

Eleven `kernel_checked` bridges: nine integer-scaffold pairs (no S/T in trace) plus two complex
S/T denotation anchors (Clifford H-H-S, phase-polynomial H-S) from B2.

**Blocked from kernel_checked:**

| Benchmark | Reason |
|-----------|--------|
| `rx_gate_equivalence_small_instance` | Lean proof uses H scaffold; QASM trace is RX(π/2) |

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

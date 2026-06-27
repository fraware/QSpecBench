# Research and infrastructure roadmap

QSpecBench separates **infrastructure** (schema, validators, honest labels) from **scientific
results** (full protocol proofs). The dashboard counts each honestly.

## Infrastructure (tooling milestones)

- [x] Wire artifact JSON through schema validation in `qspecbench validate` (B5)
- [x] Bridge taxonomy: `manifest_checked_theorem_binding` vs `python_denotation_consistency` (P0)
- [x] Structured Lean evidence anchors for manifest bridges (P0)
- [x] Fail-closed QASM extraction with `qasm_extraction` policy (P0)
- [x] QEC granular `qec_claim_scope` + unknown label hard-fail (P0)
- [x] Expand `bridge_theorem_manifest.json` to 11 manifest-checked pairs
- [x] Align Lean `ComplexGate` with Python for S/T; complex-scaffold manifest bridges
- [x] QEC `single_pauli_error_correction_validator` brute-force logical preservation
- [x] OpenQASM `rz`/`ry`/`cz`/`u`/`cp` in Python matrix extractor
- [x] Release bundle CLI stub (`qspecbench release-bundle`)
- [ ] Second proof assistant in CI (Coq/Rocq/Isabelle beyond stubs)

### Manifest bridge status (2026-06-27)

Eleven `manifest_checked_theorem_binding` bridges (integer + complex scaffolds). Three
`python_denotation_consistency` bridges. Zero `kernel_checked_artifact_semantics`.

**Blocked from manifest binding:**

| Benchmark | Reason |
|-----------|--------|
| `rx_gate_equivalence_small_instance` | Lean uses parser plumbing scaffold; QASM trace is RX(π/2) |

## P1 deferred (post-P0)

| Item | Notes |
|------|-------|
| First `kernel_checked_artifact_semantics` bridge | Requires real artifact-semantics Lean proof, not manifest binding |
| Teleportation `reference_claim` | Full protocol + measurement feed-forward semantics |
| QEC correction `reference_claim` | Decoder + logical preservation checked, not assumed tables |
| Distance proofs | Bruteforce `distance_result` wired to checked status for small codes |
| Hamiltonian corpus v0.2.0 | Migrate remaining untyped `hamiltonian.json` artifacts |
| README status auto-sync | Extend `scripts/sync_readme_maturity.py` to pull dashboard summary block |
| RX(π/2) vs H | Separate Lean denotation for parameterized RX, not H scaffold |

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

Promoting any of these to `reference_claim` before the proof exists would violate the project's core
honesty rule.

# Benchmark paper outline (draft framing)

Target venue: methods / infrastructure track (not a "we proved quantum computing" paper).

## Title (working)

QSpecBench: A Shared, Honest Benchmark Suite for Quantum Correctness Claims

## Abstract (one paragraph)

Quantum software stacks make heterogeneous correctness claims — circuit equivalence, error correction, simulation bounds — checked with incompatible tooling and vocabulary. QSpecBench packages each claim as a reviewable benchmark: informal statement, machine spec, artifacts, evidence, and an explicit trust boundary. We report corpus maturity honestly: most entries are reference scaffolds; a growing set of scoped `reference_claim` benchmarks have fully checked obligations under declared semantics. The suite separates schema, tooling, and corpus versions so infrastructure progress does not imply scientific proof.

## 1. Introduction

- Problem: claim / evidence / scope conflation in papers and tools
- Goal: shared vocabulary + honest labels, not a single proof assistant
- Contributions: schema v0.2, validators, manifest bridges, QEC granular scope, dashboard

## 2. Claim model

- `spec.yaml` structure: claim_scope, proved_scope, headline_claim_status
- Maturity ladder: seed → usable → reference_scaffold → reference_claim
- Trust levels and evidence types

## 3. Infrastructure (what we built)

- Validators, CI (Lean, QCEC, SMT, provenance drift, claim_diff freshness)
- Manifest-checked theorem binding vs python denotation consistency vs kernel artifact semantics
- Release bundles and reproducibility manifest

## 4. Scoped reference claims (what is actually proved today)

**Corpus v0.2.0 snapshot (48 benchmarks):**

| Metric | Count |
|--------|------:|
| `reference_claim` (fully checked headline obligations) | 8 |
| `reference_scaffold` | 30 |
| `usable` | 7 |
| Manifest-checked theorem bindings | 11 |
| Python denotation consistency bridges | 3 |
| Kernel-checked artifact semantics | 0 |
| Kernel-checked codegen-trace bridges | 6 |

**The eight `reference_claim` benchmarks:**

| ID | Track | Checked under |
|----|-------|---------------|
| `bell_state_preparation` | algorithms | `int_scaffold`, finite matrix |
| `qft_then_inverse_qft_identity_up_to_ordering` | algorithms | `int_scaffold`, finite matrix |
| `swap_from_three_cx` | algorithms | `int_scaffold`, finite matrix |
| `cnot_self_inverse_cancellation` | equivalence | manifest bridge + Lean kernel |
| `hadamard_conjugates_x_to_z` | equivalence | manifest bridge + Lean kernel |
| `single_qubit_gate_cancellation` | equivalence | manifest bridge + Lean kernel |
| `qft_inverse_qft_small_instance` | equivalence | manifest bridge + Lean kernel |
| `small_fermionic_hamiltonian_is_hermitian` | hamiltonian | Pauli artifact hermiticity |

Each row's `checked_under` / `not_checked_under` fields appear in `spec.yaml` `headline_claim_status` and the [dashboard](status.md).

- Equivalence / algorithm examples under `int_scaffold` / `complex_scaffold`
- Hamiltonian hermiticity under Pauli artifact model
- QEC: structure + table checks + logical preservation brute force (not full protocol proofs; bit-flip scaffold with assumed decoder)

## 5. Open research benchmarks (honest gaps)

- Teleportation, Grover, no-cloning, full QEC decoder proofs, analytic Trotter bounds
- First `kernel_checked_artifact_semantics` bridge (codegen pilot for CNOT; kernel proof gap — see `docs/bridge_codegen_design.md`)

## 6. Community and governance

- Dual review for `reference_claim`, track maintainers, promotion checklist
- External QEC certificate envelope (`schema/qec_external_certificate.schema.json`) for scalable proofs
- Stub proof-assistant adapters (Coq/Rocq/Isabelle) with CI smoke tests; Lean 4 remains sole kernel

## 7. Related work

**Circuit equivalence and verification tools.** QCEC (Muhammad et al., 2022) provides
exact equivalence checking for quantum circuits and is used in QSpecBench for external
equivalence evidence on compiler-style benchmarks. Qiskit’s transpiler stack documents
equivalence checking via third-party tools rather than a single proof-carrying format;
QSpecBench complements this with explicit claim scope and maturity labels.

**Interactive theorem proving.** Lean 4 with Mathlib supplies the sole kernel-checked
denotation layer in the corpus (OpenQASM3 gate traces, Pauli matrices, small QEC scaffolds).
The QuantumInfo library ecosystem in Rocq/Coq (e.g., Voigt’s quantum library developments)
and Isabelle/HOL quantum entries remain stub adapters in QSpecBench — optional second-assistant
CI is gated on `QSPECBENCH_COQ=1`.

**QEC certificate formats.** Stabilizer tableau tools (e.g., Stim-style detector models)
and distance-prover pipelines (SAT/SMT encodings) motivate the external certificate envelope
(`qec_external_certificate.schema.json`). QSpecBench does not claim these external proofs
are kernel-checked; linkage is via SHA256 artifact hashes and honest `qec_certificate_level`.

**Benchmark suites for quantum software.** Prior quantum benchmark collections focus on
performance, noise, or algorithmic heuristics rather than machine-readable proof obligations.
QSpecBench’s contribution is schema + validators + honest maturity, not a replacement for
domain-specific formalizations (e.g., full protocol security proofs in cryptography).

**Dynamic circuit semantics.** OpenQASM 3 classical control and measurement are documented
in the language specification; QSpecBench operational semantics (`dynamic_simulator.py`) are
explicitly Python-only with a four-qubit limit until Lean projective-update rules exist.

## 8. Conclusion

Infrastructure first; scoped reference claims as they close; no maturity inflation.

## Appendix

- Schema reference, example benchmark walkthrough, CI matrix
- Bridge codegen hash pipeline (`ast_sha256`, `generated_lean_sha256`, `bridge-codegen verify`)
- Compiler equivalence gaps (Clifford / phase-polynomial source vs target manifests)
- RX(π/2) phase convention (`benchmarks/equivalence/rx_gate_equivalence_small_instance/notes/semantic_bridge.md`)

## Submission checklist (target)

| Section | Status |
|---------|--------|
| Abstract + honest maturity counts | Draft complete |
| Claim model + trust boundaries | Draft complete |
| Infrastructure + CI matrix | Needs figure |
| Eight reference_claim case studies | Draft table |
| Open gaps (kernel artifact semantics, dynamic QASM) | Draft complete |
| Related work bibliography | Draft with real tool/library citations |
| Artifact / release bundle citation | v0.2.0 tagged |

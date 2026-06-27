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

- Equivalence / algorithm examples under `int_scaffold` / `complex_scaffold`
- Hamiltonian hermiticity under Pauli artifact model
- QEC: structure + table checks + logical preservation brute force (not full protocol proofs)

Report counts from dashboard; include `checked_under` / `not_checked_under` tables.

## 5. Open research benchmarks (honest gaps)

- Teleportation, Grover, no-cloning, full QEC decoder proofs, analytic Trotter bounds
- First `kernel_checked_artifact_semantics` bridge (blocked on codegen — see `docs/bridge_codegen_design.md`)

## 6. Community and governance

- Dual review for `reference_claim`, track maintainers, promotion checklist

## 7. Related work

- Proof-assistant libraries, QCEC/Qiskit verification, QEC formalizations

## 8. Conclusion

Infrastructure first; scoped reference claims as they close; no maturity inflation.

## Appendix

- Schema reference, example benchmark walkthrough, CI matrix

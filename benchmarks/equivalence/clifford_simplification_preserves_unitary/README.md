# Clifford simplification preserves unitary

## Claim

A Clifford simplification pass preserves the circuit unitary on declared registers.

## Why this matters

Compiler equivalence representative for Clifford circuits.

## Objects

- source/target QASM

## Specification

Exact unitary equality; ancillae/garbage per preconditions.

## Evidence

- See `spec.yaml` evidence block; seed benchmarks may have no checked proof.

## Trust boundary

Explicit in `spec.yaml` trust_boundary; no unsupported verification claims.

## Status

Current maturity: **reference_scaffold**.

## Known gaps

Lean kernel anchor proves complex OpenQASM3 denotation of the **source** gate trace (H H S on one
qubit), aligned with Python `qasm_matrix` for S/T phases. It does **not** prove source/target QASM
equivalence or full compiler simplification correctness (`semantic_correctness_of_circuit_vs_claim`
remains open). Maturity stays **reference_scaffold** until that obligation is discharged.

## References

- (add references when promoting beyond seed)
## Claim diff

See evidence/claim_diff.md for declared vs checked obligation gap (Section C).

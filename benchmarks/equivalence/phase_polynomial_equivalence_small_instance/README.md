# Phase polynomial equivalence (small instance)

## Claim

Two circuits realize the same phase polynomial on a small declared instance.

## Why this matters

Phase-polynomial equivalence track for compiler researchers.

## Objects

- source/target QASM

## Specification

Relational equivalence on phase polynomial representation.

## Evidence

- See `spec.yaml` evidence block; seed benchmarks may have no checked proof.

## Trust boundary

Explicit in `spec.yaml` trust_boundary; no unsupported verification claims.

## Status

Current maturity: **reference_scaffold**.

## Known gaps

Lean kernel anchor proves complex OpenQASM3 denotation of the **source** gate trace (H S on one
qubit), aligned with Python for S phase on |1⟩. Phase-polynomial equivalence between source and
target circuits and the full relational claim remain open
(`semantic_correctness_of_circuit_vs_claim`). Maturity stays **reference_scaffold**.

## References

- (add references when promoting beyond seed)
## Claim diff

See evidence/claim_diff.md for declared vs checked obligation gap (Section C).

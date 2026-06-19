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

Current maturity: **reference**.

## Known gaps

Kernel-checked proof or stronger tool evidence may be required for reference maturity.

## References

- (add references when promoting beyond seed)

# Single-qubit gate cancellation

## Claim

Consecutive inverse single-qubit gates on the same wire cancel to identity.

## Why this matters

Minimal equivalence pattern for compiler peephole rules.

## Objects

- `artifacts/source.qasm`, `artifacts/target.qasm`

## Specification

Exact unitary equality; no ancillae; no measurements.

## Evidence

- See `spec.yaml` evidence block; seed benchmarks may have no checked proof.

## Trust boundary

Explicit in `spec.yaml` trust_boundary; no unsupported verification claims.

## Status

Current maturity: **seed**.

## Known gaps

Kernel-checked proof or stronger tool evidence may be required for reference maturity.

## References

- (add references when promoting beyond seed)

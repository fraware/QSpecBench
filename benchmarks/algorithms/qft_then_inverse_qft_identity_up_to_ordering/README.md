# QFT then inverse QFT is identity up to ordering

## Claim

Applying QFT followed by inverse QFT yields the identity on the declared register up to bit-ordering conventions.

## Why this matters

Tests algorithm identity claims with ordering conventions explicit.

## Objects

- `artifacts/circuit.qasm`

## Specification

Exact algorithm identity; ordering conventions must be read from assumptions.

## Evidence

- See `spec.yaml` evidence block; seed benchmarks may have no checked proof.

## Trust boundary

Explicit in `spec.yaml` trust_boundary; no unsupported verification claims.

## Status

Current maturity: **usable**.

## Known gaps

Kernel-checked proof or stronger tool evidence may be required for reference maturity.

## References

- (add references when promoting beyond seed)

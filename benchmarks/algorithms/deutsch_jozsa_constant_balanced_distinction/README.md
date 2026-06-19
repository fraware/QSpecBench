# Deutsch–Jozsa distinguishes constant from balanced oracles

## Claim

The Deutsch–Jozsa circuit accepts constant oracles and rejects balanced ones for the declared small instance.

## Why this matters

Oracle-based algorithm benchmark with explicit oracle semantics.

## Objects

- `artifacts/circuit.qasm` — DJ circuit with oracle placeholder

## Specification

Oracle-based, fixed-size exact decision claim on measurement outcome.

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

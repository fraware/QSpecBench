# Superdense coding decodes two classical bits

## Claim

A shared Bell pair and one qubit transmission let Bob decode two classical bits after a Bell measurement and Pauli correction.

## Why this matters

Introductory protocol linking entanglement, dense coding, and measurement semantics.

## Objects

- `artifacts/circuit.qasm` — superdense coding circuit scaffold

## Specification

Exact relational claim on decoded classical bits; fixed 2+1 qubit profile.

## Evidence

- QASM syntax parse
- Lean 4 kernel Bell-pair preparation scaffold (`superdense_bell_pair_entangled`)

## Trust boundary

Explicit in `spec.yaml` trust_boundary; relational decoding and measurement remain outside kernel scope.

## Status

Current maturity: **reference**.

## References

- (add references when promoting beyond seed)

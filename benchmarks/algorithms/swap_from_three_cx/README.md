# SWAP from three CNOT gates

## Claim

Three CNOT gates in standard order implement SWAP on two qubits.

## Why this matters

Standard circuit identity for routing and compilation tracks.

## Objects

- `artifacts/source.qasm`, `artifacts/target.qasm`

## Specification

Exact unitary equivalence.

## Evidence

Lean kernel bridge (`bridge_hadamard_cancel`), verify-bridge, QASM parse, QCEC.

## Trust boundary

See spec.yaml.

## Status

Current maturity: **reference_claim**.

## Known gaps

Unitary equivalence beyond declared gate subset remains an unproved obligation.

## References

- (add references when promoting beyond usable)

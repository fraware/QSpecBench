# CNOT self-inverse cancellation

## Claim

Two consecutive CNOT gates on the same control-target pair implement the identity on the declared two-qubit register.

## Why this matters

Minimal **equivalence** benchmark for compiler peephole optimization with an independently checkable certificate on a fixed instance.

## Objects

- `artifacts/source.qasm` — CX.CX circuit
- `artifacts/target.qasm` — empty circuit (identity)
- `evidence/unitary_equality.certificate.json` — checkable certificate

## Specification

Exact unitary equality; no ancillae, garbage, measurements, or parameterized gates. Qubit ordering: `q[0]` control, `q[1]` target.

## Evidence

- QASM syntax checks (passing; syntax only)
- **Lean 4 kernel proof** `QSpecBench.CNOT.cnot_mul_self` (passing; checked via `lake build`)
- Independently checkable unitary certificate (supplementary)
- QCEC equivalence (not checked in CI)

## Trust boundary

Lean 4 kernel checks the matrix-model theorem. Certificate provides independent small-instance verification. Matrix model is not proved equivalent to full QASM semantics for all circuits.

## Status

Current maturity: **reference_claim**.

## Known gaps

- General n-qubit proof in a proof assistant
- QCEC integration in CI for larger instances

## References

- Standard self-inverse property of CNOT

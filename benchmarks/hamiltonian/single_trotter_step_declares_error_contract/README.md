# Single Trotter step proves entry-modulus error bound

## Claim

Hamiltonian simulation claim: a single first-order product-formula step at dt=0.1 achieves a proved entry-modulus error bound of 1/5 (discharged in Lean); historical fidelity 1e-6 at dt=0.1 remains permanently not-applicable (proved-negative); a revised Taylor-proxy fidelity 1e-6 at dt=1/100 is checked.

## Why this matters

Scientific-intent Hamiltonian benchmark with a discharged analytic entry-modulus bound
and an honest fidelity resolution (historical gap permanent; revised step checked).

## Objects

- `artifacts/hamiltonian.json`

## Specification

Approximate mode with metric `entry_modulus` and bound `0.2` at dt=0.1.

## Evidence

- Lean kernel discharge of entry-modulus + Mathlib Euclidean ell^2 opNorm packaging
- Revised Taylor-proxy fidelity at dt=1/100
- Dual hash-bound formal/domain reviews (proposition v2)

## Trust boundary

**Checked under:** entry-modulus analytic bound at the artifact step; revised Taylor-proxy fidelity at dt=1/100.

**Not checked under:** historical fidelity 1e-6 at dt=0.1 (permanent proved-negative); state fidelity beyond Taylor proxy.

## Status

Current maturity: **reference_claim**.

## Known gaps

Historical fidelity 1e-6 at artifact step remains permanently not_applicable.
Taylor proxy is not full state fidelity.

## References

- (product-formula / Trotter error literature)

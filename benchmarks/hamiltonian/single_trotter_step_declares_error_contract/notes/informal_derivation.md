# Informal derivation — single Trotter step error contract

## Declared contract (rewritten)

- Metric: `entry_modulus` (modulus of matrix entry (0,1) of U−V)
- Bound: `0.2` (= 1/5) at step time Δt = 0.1
- Discharged by `product_formula_entry_discharges_declared_bound_at_step` /
  `single_trotter_step_declares_entry_error_contract`

## Historical fidelity gap

The previous fidelity bound 1e-6 at Δt=0.1 is **proved false** under the Taylor
Frobenius-squared proxy (`taylor_at_artifact_step_exceeds_fidelity_ceiling`).
It remains in `unproved_obligations` with status `not_applicable` as a historical
negative, not as a checked claim.

## Operator-norm / Frobenius note

Proved packaging for the noncommuting X+Z product formula:

- F²(U)=F²(V)=2 exactly; hence ‖U−V‖_F ≤ √8 for all t (closed-form)
- |D₀₁| ≤ ‖D‖_F ≤ √8 spectral sandwich seed
- Mathlib ℓ∞ `ContinuousLinearMap.opNorm` wired via
  `mathlibLinftyOpNorm_eq_ContinuousLinearMap_opNorm`
- Mathlib Euclidean ℓ² `mathlibL2OpNorm` = `toEuclideanLin` CLM opNorm with
  ‖D‖₂ ≤ ‖D‖_F ≤ √8 (`mathlib_spectral_opNorm_equality`)
- entry ≤ C|t|³ on |t|≥0.1 with spectral-seed packaging constant C'=5000

Headline required obligations are the entry-modulus contract (discharged).
Fidelity 1e-6 remains historical proved-negative only. Maturity is
`experimental_closed` (formerly `reference_claim` as of v0.2.x under dual hash-bound
reviews; demoted for v1 — not gold / independently reviewed).

## Multi-step Trotter composition (side obligation)

Declared finite step count N=5 composed with the single-step entry-modulus
bound (ε=1/5) via a triangle-inequality proxy on identical nonnegative bounds:
N·ε=1 (`multi_step_entry_composition_identity`), bundled with the single-step
discharge into `multi_step_trotter_composition_discharged`. This is a declared,
finite-N composition — not an operator-norm / diamond process-distance Trotter
composition theorem and not a claim about unbounded step count.

## Haar Monte-Carlo integral (side obligation)

`evidence/haar_monte_carlo_cert.py` draws 256 Haar-distributed qubit states
(deterministic seed) and estimates the average gate fidelity of Pauli-X vs
identity; the sample mean agrees with the Nielsen closed form 1/3 within the
declared absolute tolerance 1/50, and the certificate emits a sha256 over its
own deterministic payload (never a bare success string). The Lean theorem
`haar_monte_carlo_integral_contract` records the matching declared contract
parameters (256 samples, tolerance 1/50) and that the Nielsen closed form
equals 1 at product-formula exactness — the reference value the certificate is
checked against. This numerical certificate plus declared-parameter Lean anchor
discharges `haar_monte_carlo_integral` under the declared certificate scope; it
is not a Lean / measure-theoretic proof of the Haar integral itself.

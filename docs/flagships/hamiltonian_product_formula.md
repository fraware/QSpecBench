# Flagship specification: operator-level Hamiltonian product-formula bound

Status: **required scientific target; not yet a completed proof.** See issue #17.

Existing entry-modulus/numerical certificates remain valid only for their declared scope. They do not satisfy this stronger target.

## Proposition target

For an explicit finite-dimensional noncommuting Hamiltonian decomposition `H = A + B` (or a precisely declared finite sum), prove a checked operator-level bound for first-order product-formula simulation, parameterized meaningfully by total evolution time `t` and step count `r`.

A canonical target shape is:

`||exp(-i t (A+B)) - (exp(-i t A/r) exp(-i t B/r))^r||_op <= C(A,B) * t^2 / r`

The final exact theorem may use a sharper constant/shape, but the metric, dimensional assumptions and parameter regime must be explicit.

## Required obligations

1. `hamiltonian_artifact_parse` — pinned source Hamiltonian artifact parses to the declared mathematical object.
2. `hermiticity` — terms and total Hamiltonian meet the hypotheses of the evolution theorem.
3. `decomposition_correct` — source mapping/Pauli decomposition equals the declared Hamiltonian.
4. `product_formula_definition` — emitted step/circuit denotes the intended product formula.
5. `analytic_error_bound` — operator-level approximation theorem under explicit hypotheses.
6. `parameter_instantiation` — concrete benchmark parameters satisfy theorem hypotheses.
7. `multi_step_composition` — relation between one-step error and the `r`-step proposition is formally justified, not merely named.
8. `artifact_to_circuit_binding` — emitted circuit/artifact is hash-bound to the formally analyzed product formula.

## Non-substitutes

The following are supporting evidence only:
- entry-wise matrix modulus bounds;
- a finite numerical Haar sample;
- an `N * epsilon` bookkeeping statement without the operator-level theorem;
- equality/error for a single fixed `dt` with no meaningful time/step parameterization;
- simulation results alone.

## Promotion gate

The flagship requires a closed assurance graph, explicit metric and domain, kernel-checked analytic theorem, artifact mapping/circuit binding, authenticated formal/domain reviews, and exact-head release verification.

# Claim diff: single_trotter_step_declares_error_contract

<!-- scope_fingerprint: d35bdd1c91ae58071eae65a31d407d030cb14149634e221211050e75dd8293c2 -->

**Maturity:** experimental_closed
**Headline status:** checked

## Informal claim (README/spec)
Hamiltonian simulation claim: a single first-order product-formula step at dt=0.1 achieves a proved entry-modulus error bound of 1/5 (discharged in Lean); historical fidelity 1e-6 at dt=0.1 remains permanently not-applicable (proved-negative); a revised Taylor-proxy fidelity 1e-6 at dt=1/100 is checked.

## Declared headline (claim_scope)
Hamiltonian simulation claim: a single first-order product-formula step at dt=0.1 achieves a proved entry-modulus error bound of 1/5 (discharged in Lean); historical fidelity 1e-6 at dt=0.1 remains permanently not-applicable (proved-negative); a revised Taylor-proxy fidelity 1e-6 at dt=1/100 is checked.

## Required obligations
- contract_declaration
- entry_modulus_achievement

## Checked obligations
- [x] contract_declaration
- [x] entry_modulus_achievement
- [x] mathlib_spectral_opNorm_equality
- [x] fidelity_taylor_proxy_at_revised_step
- [x] process_fidelity_hs_proxy
- [x] average_gate_fidelity_hs_proxy
- [x] diamond_norm_op_upper_proxy
- [x] haar_average_gate_fidelity_unitary
- [x] diamond_norm_op_characterization
- [x] unitary_qubit_diamond_closed_form
- [x] unitary_choi_diamond_characterization
- [x] unitary_choi_schatten1_diamond
- [x] qubit_pauli_channel_cb_class
- [x] orthogonal_pure_choi_diamond
- [x] qubit_cptp_cb_proved_subclass_mathlib
- [x] multi_step_trotter_composition
- [x] haar_monte_carlo_integral

## Unproved / open obligations

## Gap
- None among declared required obligations.

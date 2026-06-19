# Trotter error contract

This benchmark declares an **approximate** simulation claim for a single first-order Lie-Trotter step:

- Product-formula order: 1 (first-order Lie-Trotter)
- Metric: fidelity
- Bound: `1e-6` per single step (declared in `spec.yaml` and `artifacts/hamiltonian.json`)

The Hamiltonian artifact specifies a two-qubit Pauli sum used as the simulation target. The bound is a **declared contract** in the machine spec, not a kernel-checked or numeric proof that the step achieves this fidelity.

This note is human-reviewed specification context. No Lean proof or simulation certifies the bound; reference promotion requires checked evidence per the Hamiltonian track stack.

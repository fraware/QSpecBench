# Second-order Trotter bound contract

This benchmark declares a **second-order Trotter** simulation step with an operator-norm error contract stated as `O(step^3)` language in `spec.yaml` and `artifacts/hamiltonian.json`.

The contract documents the expected scaling order for a Suzuki–Trotter product formula without attaching a kernel-checked proof or numeric simulation that verifies the bound on the declared Hamiltonian instance.

Human review confirms the machine spec and artifact align on order, metric (`operator_norm`), and honest partial labeling. No formal proof of the bound is claimed.

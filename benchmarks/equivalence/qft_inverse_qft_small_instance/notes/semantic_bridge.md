# Semantic bridge: QFT / inverse QFT (2-qubit scaffold)

- **QASM:** `artifacts/source.qasm` (Hdivided QFT scaffold) and `artifacts/target.qasm` (inverse scaffold).
- **Lean:** `QSpecBench.qft2_mul_invqft2` — on the declared model, forward and inverse circuits coincide and compose to `4 • I`.

This instance uses the same unnormalized Hadamard convention as `QSpecBench.Pauli`. QCEC and the SAT certificate apply to the fixed 2-qubit instance only.

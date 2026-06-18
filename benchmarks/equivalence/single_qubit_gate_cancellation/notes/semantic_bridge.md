# Semantic bridge: single-qubit gate cancellation

- **QASM:** consecutive `h` gates on one wire vs identity scaffold.
- **Lean:** `QSpecBench.hadamard_mul_self` (`hadamard2 * hadamard2 = scale2 2 id2`).

Hadamard normalization matches the Pauli/CNOT integer model documented in the equivalence track.

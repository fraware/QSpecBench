# Semantic bridge: Hadamard conjugates X to Z

- **QASM:** `artifacts/source.qasm` (HXH) vs `artifacts/target.qasm` (Z up to phase).
- **Lean:** `QSpecBench.hadamard_conjugates_x` on the unnormalized integer Hadamard model (`H*H = 2I`, `H X H = 2Z`).
- **Normalization:** OpenQASM `h` includes `1/sqrt(2)` scaling; Lean model uses integer matrices with explicit factors documented in `expected/semantic_bridge.json`.

Link status: `documented_not_proved` until OpenQASM gate semantics are formalized in Lean.

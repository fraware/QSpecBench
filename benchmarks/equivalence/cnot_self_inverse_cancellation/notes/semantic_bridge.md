# Semantic bridge: CNOT self-inverse

This benchmark pairs OpenQASM `cx` gates with the Lean 4 matrix model in `QSpecBench.CNOT`.

- **QASM artifacts:** `artifacts/source.qasm` (CX CX) and `artifacts/target.qasm` (empty / identity scaffold).
- **Lean anchor:** `QSpecBench.cnot_mul_self` — proves `cnot4 * cnot4 = id4` on the declared 4×4 model.
- **Normalization:** CNOT is the standard control-on-0, target-on-1 permutation matrix; no global phase factors.

`claimed_link` remains `documented_not_proved`: kernel-checked equality is on the Lean integer model, not a formal OpenQASM semantics embedding.

QCEC equivalence (when run) and the SAT matrix certificate narrow the practical gap for this fixed instance.

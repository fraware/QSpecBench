# Toffoli pair equivalence policy

## Kernel-checked (partial)

- **Source CCX:** `bridge_toffoli_codegen_ccx` (int scaffold) and `bridge_toffoli_codegen_ccxC`
  (complex `denotateOps3C` on CCX trace).
- **Target decomposition:** codegen + parse theorem
  `parseQasmSource_toffoli_target_kernel_eq_generated_ops`; complex denotation via `denotateOps3C`
  (H/T/Tdg/CX on three qubits).
- **Scoped C2 pair bridge** (`semantic_bridge.pair_lean_theorem`):
  `QSpecBench.Quantum.OpenQASM3Parser.bridge_toffoli_ccx_eq_target_decomposition` — conjunction of
  source CCX denotation on the int scaffold and target artifact parse bound. This is **not** a
  `denotateOps3C` source = target denotation theorem.

## Open (blocks pair promotion)

- **No Lean theorem** `denotateOps3C source_ops = denotateOps3C target_ops` (exact or global phase).
- Unnormalized `qasm_matrix` model: source CCX permutation ≠ target decomposition matrix
  (verified in Python; 10/64 differing entries).
- QCEC equivalence uses physical unitary semantics (global phase); not closed in Lean.

## Honest scope

Headline is **artifact_bound_reference_claim** (source CCX only). Pair equivalence
(`denotateOps3C source = target`, exact or global phase) remains open; see
`evidence/source_target_pair_open.lean`. QCEC certifies physical equivalence externally;
target decomposition trace is manifest-hashed for future pair proof work.

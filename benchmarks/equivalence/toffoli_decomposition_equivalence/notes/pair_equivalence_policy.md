# Toffoli pair equivalence policy

## Kernel-checked

- **Source CCX:** `bridge_toffoli_codegen_ccx` (int scaffold) and `bridge_toffoli_codegen_ccxC`
  (complex `denotateOps3C` on CCX trace) — also checked on sibling
  `native_ccx_artifact_denotes_toffoli_unitary`.
- **Target decomposition:** codegen + parse theorem
  `parseQasmSource_toffoli_target_kernel_eq_generated_ops`.
- **Normalized Clifford+T pair equality (headline):**
  `QSpecBench.Quantum.OpenQASM3.bridge_toffoli_decomposition_normalized_exact`
  — elaborator-exported kernel bridge; both sides equal `ccx8C` under
  `denotateOps3C_normalized` (LSB wires, algebraic H/T).
- **Phase policy:** `ToffoliDecomposition.toffoli_normalized_global_phase_policy`
  (`ExactDenotationEq` ⇒ `EquivUpToGlobalPhase` with φ = 0).
- **Wire order:** `bridge_toffoli_decomposition_wire_order_lsb` under
  `openqasm_little_endian_wire_order`.
- **Gate-atom bridges:** `hadamardN_toComplex`, `tGateCT_toComplex`, `tDagGateCT_toComplex`
  (CT atoms match ComplexGate normalized / `Complex.exp` T/T†). Composition fold is the
  declared trusted denotation for this claim (`cliffordTDenotationTrustNote`).

## Models and endianness

- Lean 3-qubit `kron3` / `cnot8Col`: qubit 0 = LSB (bit weight 1).
- Lean 2-qubit `kron2I` / default Python `qasm_matrix._apply_single`: **legacy** order
  (qubit 0 on the high Kronecker factor) for verify-bridge alignment on 2-qubit pilots.
- Unnormalized Hadamard in default Python extraction: with LSB embeds, target = 2 · CCX
  (two H factors); exact unnormalized `denotateOps3C` source = target remains **out of scope**.

## Honest scope

Maturity: `experimental_closed` under the **narrowed** informal claim
(normalized CT denotation, exact equality; formerly ABRC as of v0.2.x, demoted for v1).
Residual not-checked labels include
unnormalized pair equality and default Python 3-qubit legacy Kron.

# Normalized / global-phase policy (Clifford simplification)

## Models

| Model | H gate | Source HHS vs target S |
|-------|--------|------------------------|
| `qasm_matrix` (manifest) | Unnormalized integers `(1,1;1,-1)` | `denotateOps1C source = 2 · denotateOps1C target` |
| Physical unitary (QCEC) | Includes `1/√2` per H | Equivalent up to global phase (external) |
| `hadamardC_normalized` (Lean) | `H / √2` per gate | Exact matrix equality (see `hadamardC_normalized_mul_self`) |

## Chosen kernel policy

**`compiler_trace_scaled` (factor 2):** under the complex denotation matching Python
`qasm_matrix`, the simplification pass relates source and target by a scalar factor of 2
because `H·H = 2·I` in the unnormalized model.

Kernel theorem: `QSpecBench.Quantum.OpenQASM3.bridge_clifford_source_target_scaled`.

Exact entry-wise equality `denotateOps1C clifford_hhs = denotateOps1C clifford_s_single` is
**false** in the unnormalized model; QCEC certifies physical unitary equivalence externally.

## Dual-manifest status

Target-side codegen hashes are pinned (`target_lean_theorem`, `target_gate_trace_sha256`).
`pair_lean_theorem` = `bridge_clifford_source_target_scaled` is kernel-checked under the factor-2
policy above. **Not earned:** `kernel_checked_codegen_trace` dual-manifest verify-bridge on both
artifacts under one normalized gate model (exact matrix equality is false in the unnormalized model).

## Promotion

`claimed_link` remains `manifest_checked_theorem_binding` (dual-manifest source anchor + scaled
pair theorem). Maturity stays **reference_scaffold** until normalized dual-manifest verify-bridge
closes the compiler headline gap.

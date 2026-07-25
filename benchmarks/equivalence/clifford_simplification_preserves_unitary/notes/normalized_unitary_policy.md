# Normalized / global-phase policy (Clifford simplification)

## Models

| Model | H gate | Source HHS vs target S |
|-------|--------|------------------------|
| `qasm_matrix` (unnormalized manifest legacy) | Unnormalized integers `(1,1;1,-1)` | `denotateOps1C source = 2 * denotateOps1C target` |
| Physical unitary (QCEC) | Includes `1/sqrt(2)` per H | Equivalent up to global phase (external) |
| `hadamardC_normalized` (Lean, headline) | `H / sqrt(2)` per gate | Exact matrix equality (see `hadamardC_normalized_mul_self`) |

## Chosen kernel policy (promoted)

**`normalized_source_target_exact`:** under `denotateOps1C_normalized` (the physical-unitary
Hadamard, matching the Python `qasm_matrix` extraction used by `verify-bridge`), the source
trace `H H S` and target trace `S` denote the *same* matrix exactly. `H . H = I` under the
normalized model, so the two Hadamards on the source cancel and the residual `S` gate is
identical to the target circuit.

Kernel theorem: `QSpecBench.Quantum.OpenQASM3.bridge_clifford_source_target_normalized_exact`.

The legacy unnormalized relation `denotateOps1C clifford_hhs = 2 * denotateOps1C clifford_s_single`
(`bridge_clifford_source_target_scaled`, `H . H = 2 * I` in the unnormalized integer model)
remains kernel-checked as a documented, non-headline fact; it is **not** claimed as the
compiler-equivalence headline.

## Dual-manifest status (closed)

Both source and target codegen hashes are pinned (`target_lean_theorem`,
`target_gate_trace_sha256`, `target_artifact_parse_theorem`). `verify-bridge` runs on the source
artifact against the same normalized (physical-unitary) gate model used by the Lean kernel
theorem; `bridge-codegen verify` cross-checks both manifest entries against on-disk artifact and
AST hashes.

## Promotion

`claimed_link` is `kernel_checked_artifact_semantics` (dual-manifest source/target codegen +
elaborator-bound normalized pair theorem + BridgeMetadata pin). Maturity is
**artifact_bound_reference_claim**. Residual not-checked labels: unnormalized `denotateOps1C`
exact pair equality (factor 2), `full_openqasm3`, `hardware_semantics`.

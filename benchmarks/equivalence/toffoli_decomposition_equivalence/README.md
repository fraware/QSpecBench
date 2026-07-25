# Toffoli decomposition equivalence

## Claim

Under the normalized Clifford+T denotation (LSB wires, algebraic H/T), the declared
H/T/CX decomposition and native CCX artifact have identical denotations (exact
equality; global phase φ = 0).

## Why this matters

Compiler decomposition track. Native CCX denotation remains separately checked on
`native_ccx_artifact_denotes_toffoli_unitary`; this entry is the source/target pair
under the CT normalized model.

## Objects

- `artifacts/source.qasm` — native CCX
- `artifacts/target.qasm` — H/T/CX decomposition

## Specification

Exact matrix equality under `denotateOps3C_normalized` (trusted composition semantics
for this claim). Gate atoms H/T/Tdg match ComplexGate normalized / `Complex.exp` matrices.

## Evidence

- QASM syntax checks (passing)
- QCEC on source/target pair (supporting external)
- Lean pair bridge: `evidence/toffoli_pair_bridge.lean`
- verify-bridge: `evidence/bridge_verify.result.json`
- Policy: `notes/pair_equivalence_policy.md`

## Trust boundary / checker chain

Checked obligations:

- `source_artifact_parse`
- `target_artifact_parse`
- `source_denotation`
- `target_denotation`
- `source_target_equivalence`
- `global_phase_policy`
- `wire_order_alignment`

Not claimed: unnormalized `denotateOps3C` pair equality; default Python 3-qubit legacy Kron.

## Status

Current maturity: **artifact_bound_reference_claim** (`kernel_checked_artifact_semantics`).

## Known gaps

- Unnormalized `denotateOps3C` exact source = target (intentionally out of scope)
- Full OpenQASM 3 / hardware semantics

## References

See `notes/pair_equivalence_policy.md` and sibling `native_ccx_artifact_denotes_toffoli_unitary`.

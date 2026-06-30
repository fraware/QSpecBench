# Clifford simplification preserves unitary

## Claim

A Clifford simplification pass preserves the circuit unitary on declared registers.

## Why this matters

Compiler equivalence representative for Clifford circuits.

## Objects

- source/target QASM

## Specification

Exact unitary equality; ancillae/garbage per preconditions.

## Evidence

- See `spec.yaml` evidence block (QCEC, source anchor, verify-bridge, scaled pair scaffold in
  `evidence/source_target_equivalence_open.lean`).

## Trust boundary

Explicit in `spec.yaml` trust_boundary; no unsupported verification claims.

## Status

Current maturity: **reference_scaffold**.

## Known gaps

Lean kernel anchor proves complex OpenQASM3 denotation of the **source** gate trace (H H S on one
qubit), aligned with Python `qasm_matrix` for S/T phases. **Scaled pair relation** under the
unnormalized model: `denotateOps1C clifford_hhs = 2 · denotateOps1C clifford_s_single`
(`bridge_clifford_source_target_scaled`; see `notes/normalized_unitary_policy.md`). Exact matrix
equality is false in that model; QCEC certifies physical unitary equivalence externally. Full
compiler simplification headline (`semantic_correctness_of_circuit_vs_claim`) remains open.
Maturity stays **reference_scaffold** until normalized dual-manifest verify-bridge closes the gap.

## References

- (add references when promoting beyond seed)
## Claim diff

See evidence/claim_diff.md for declared vs checked obligation gap (Section C).

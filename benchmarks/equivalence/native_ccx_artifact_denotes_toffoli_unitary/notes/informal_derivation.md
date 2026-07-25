# Informal derivation

The declared native CCX artifact (`artifacts/source.qasm`) is a single
three-qubit `ccx` instruction with no decomposition. Its denotation follows
directly from the standard Toffoli truth table: `ccx a, b, c` flips the target
qubit `c` iff both control qubits `a` and `b` are `|1>`, and acts as identity
on every other basis state. The declared finite matrix semantics for `ccx`
already encodes this truth table, so the codegen gate trace for the artifact
is exactly `[ccx(0, 1, 2)]` and its denotation is the 8x8 permutation matrix
for the standard Toffoli unitary.

This is checked at the kernel level via `bridge_toffoli_codegen_ccx`, which
relates `parseQasmSourceToOps` on the artifact bytes to the generated ops list
in `QSpecBench.Generated.ToffoliDecompositionEquivalence`, and via
`bridge_ccx_single`, which relates the single-instruction codegen trace to the
declared Toffoli matrix directly. No gate cancellation, rotation synthesis, or
multi-instruction rewriting is involved, so no external equivalence checker is
needed for this claim.

## Known gaps

- This benchmark only anchors the native CCX source artifact; it makes no
  claim about any H/T/CX decomposition. Decomposition-to-target equivalence is
  tracked separately under `toffoli_decomposition_equivalence`.
- Hardware-level noise, timing, and pulse-calibration semantics are out of
  scope; only the declared finite matrix semantics is checked.

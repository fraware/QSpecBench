# Compiler equivalence gap (Clifford simplification)

## What is checked

- **Source trace**: manifest `bridge_clifford_hhs` on `artifacts/source.qasm` (H H S).
- **QCEC**: external equivalence check on source vs target QASM pair.
- **verify-bridge**: Python matrix extractor matches Lean complex denotation on the
  **source** gate trace only.

## Source vs target manifest gap

`bridge_theorem_manifest.json` lists only the **source** artifact gate trace. The target
circuit (`artifacts/target.qasm`, single S gate) is not separately manifest-bound. QCEC
certifies the pair equivalent under its semantics, but QSpecBench does not yet emit a
second manifest entry with `lean_theorem` + hashes for the target trace.

## Honest scope

Headline claim ("simplification preserves unitary") remains `partially_checked`:
compiler pass correctness is evidenced by QCEC + source anchor, not a dual-manifest
hash chain for both artifacts.

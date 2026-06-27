# Compiler equivalence gap (phase polynomial)

## What is checked

- **Source trace**: manifest `bridge_hs_gate` on `artifacts/source.qasm` (H S).
- **QCEC**: source and target QASM files are byte-identical in this small instance;
  QCEC passes trivially.
- **verify-bridge**: Python matrix matches Lean complex denotation on the source trace.

## Source vs target manifest gap

Only the source gate trace appears in `bridge_theorem_manifest.json`. For non-identical
source/target pairs, QCEC may certify equivalence while QSpecBench lacks a target-side
manifest theorem + `artifact_sha256` / `gate_trace_sha256` chain.

## Honest scope

Phase-polynomial headline claims stay `reference_scaffold` with `partially_checked`
headline status until both traces are manifest-bound or a single kernel-checked
artifact-semantics proof links each QASM file to its denotation.

# QSpecBench documentation

QSpecBench is a community-grade benchmark and evidence format for quantum formal verification.

## Core concepts

- [Claim model](claim_model.md) — claims, artifacts, evidence, proofs
- [Schema reference](schema_reference.md) — `spec.yaml` fields
- [Evidence model](evidence_model.md) — evidence types and trust
- [Trust boundaries](trust_boundaries.md) — what is checked vs assumed

## Contributing

- [Adding a benchmark](adding_a_benchmark.md)
- [Adapter protocol](adapter_protocol.md)

## Tracks

- [Algorithm track](algorithm_track.md)
- [Equivalence track](equivalence_track.md)
- [QEC track](qec_track.md)
- [Hamiltonian track](hamiltonian_track.md)
- [AI formalization track](ai_formalization_track.md)

## Lean proofs

Kernel-checked modules live in [`lean/QSpecBench/`](../lean/QSpecBench/). See [Lean setup](lean_setup.md). CI installs elan and runs `lake build`.

## Status

See [status.md](status.md) for the auto-generated dashboard.

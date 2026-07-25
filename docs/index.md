# QSpecBench documentation

QSpecBench is a scoped research benchmark and evidence format for quantum formal
verification. “Community-grade” (when the [definition of completion](definition_of_completion.md)
is met) still means selected checked claims under declared universes — **not** a
complete quantum FV standard. Permanent residuals are listed in that DoD, the
[README](../README.md), and [research_tracks.md](research_tracks.md).

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

## Status and completion

- [status.md](status.md) — auto-generated dashboard
- [definition_of_completion.md](definition_of_completion.md) — truth / technical / research / community DoD
- [research_tracks.md](research_tracks.md) — scientific leftovers and permanent N/A
- [roadmap.md](roadmap.md) — infrastructure phase history
- [reference_benchmarks.md](reference_benchmarks.md) — promotion rules and ABRC list
- [release_prep_notes.md](release_prep_notes.md) — CI/release dry-run checklist (no commit/push)
- [audit_issues.yaml](audit_issues.yaml) — audit ledger ([audit_findings.md](audit_findings.md) summarizes)

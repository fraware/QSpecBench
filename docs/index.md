# QSpecBench documentation

QSpecBench is a scoped research benchmark and evidence format for quantum formal
verification. It packages claims, artifacts, typed evidence, and explicit trust
boundaries — it is **not** a complete quantum FV standard.

At the v1 completion branch:

- **Gold / `reference_claim` / `artifact_bound_reference_claim` inventory is empty** (owner decision; see [promotion freeze](promotion_freeze.md)).
- **`experimental_closed`** means machine closure under a declared assurance graph **without** authenticated independent review.
- **Community-grade governance is not claimed** (Level B of the [definition of completion](definition_of_completion.md) is unmet).
- **Issue #9** (independent third-party cold-host reproduction) is out of v1 scope.
- Permanent scientific residuals are listed in the DoD, [README](../README.md), and [research_tracks.md](research_tracks.md).

## Core concepts

- [Claim model](claim_model.md) — claims, artifacts, evidence, proofs
- [Schema reference](schema_reference.md) — `spec.yaml` fields
- [Evidence model](evidence_model.md) — evidence types and trust
- [Trust boundaries](trust_boundaries.md) — what is checked vs assumed

## Contributing

- [Adding a benchmark](adding_a_benchmark.md)
- [Adapter protocol](adapter_protocol.md)
- [Promotion freeze](promotion_freeze.md) — why gold labels are unreachable on the v1 path

## Tracks

- [Algorithm track](algorithm_track.md)
- [Equivalence track](equivalence_track.md)
- [QEC track](qec_track.md)
- [Hamiltonian track](hamiltonian_track.md)
- [AI formalization track](ai_formalization_track.md)

## Flagships (machine-closed experimental packages)

- [Compiler transformation equivalence](flagships/compiler_transformation_equivalence.md)
- [Dynamic teleportation](flagships/dynamic_teleportation.md)
- [Hamiltonian product formula (narrowed)](flagships/hamiltonian_product_formula.md)
- [QEC bit-flip layered chain](flagships/qec_bit_flip_chain.md)

## Lean proofs

Kernel-checked modules live in [`lean/QSpecBench/`](../lean/QSpecBench/). See [Lean setup](lean_setup.md). CI installs elan and runs `lake build`.

## Status, release, and governance

- [generated_status.md](generated_status.md) — machine-generated corpus counts (source of truth)
- [status.md](status.md) — auto-generated dashboard
- [definition_of_completion.md](definition_of_completion.md) — engineering / governance / science / full-vision levels
- [release_audit_v1.md](release_audit_v1.md) — v1 ship/revise decision (**currently revise**)
- [release_v1_criteria.md](release_v1_criteria.md) — what a `v1.0` tag would claim
- [governance_verification.md](governance_verification.md) — CODEOWNERS / review / branch-protection honesty
- [interoperability_matrix.md](interoperability_matrix.md) — ecosystem adapters (generated)
- [research_tracks.md](research_tracks.md) — scientific leftovers and permanent N/A
- [reference_benchmarks.md](reference_benchmarks.md) — promotion rules (gold inventory empty at v1)
- [roadmap.md](roadmap.md) — infrastructure phase history
- [audit_findings.md](audit_findings.md) — historical audit ledger (may predate demotion; prefer live generated status)

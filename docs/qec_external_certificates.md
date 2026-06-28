# External QEC certificates (scalable format stub)

Large codes cannot rely on in-repo bruteforce. This document describes a reserved certificate
envelope for external provers; it is **not** yet accepted by `qspecbench validate`.

## Schema

See `schema/qec_external_certificate.schema.json` (`certificate_version: 0.1-stub`).

## Intended use

| `claim_kind` | Example prover | Maps to `qec_claim_scope` |
|--------------|----------------|---------------------------|
| `minimum_distance` | SAT/SMT distance tools | `distance` (when witness verified) |
| `decoder_correctness` | Custom decoder checker | `decoder_algorithm` |
| `logical_preservation` | Simulation + tableau | `logical_preservation_small_code` |
| `syndrome_extraction` | Detector graph tools | `syndrome_table` |

## Required linkage

Every certificate must pin `code_ref.artifact_sha256` to a stabilizer code artifact in the
benchmark tree. Validators will eventually require:

1. SHA256 match against `expected/provenance.json`
2. `claim_kind` compatible with spec `qec_claim_scope` promotion rules
3. Explicit `trust_boundary.assumptions_not_checked` (no silent promotion to `reference_claim`)

## Current in-repo alternative

Small instances use `qec_verifier_result.json` with embedded `distance_result` from the QEC JSON
adapter (`distance_min_weight_bruteforce`). See `distance_certificate_small_css_code`.

## Phase 3 wiring (2026-06-27)

- Schema validation for `qec_external_certificate.json` via `validate_claim_artifacts`
- Semantic validation in `tools/qspecbench/qec_external.py`:
  - `code_ref.artifact_sha256` matches on-disk artifact and `expected/provenance.json`
  - `benchmark_id` matches spec `id`
  - Stub certificates (`0.1-stub`) cannot claim `result.status=proved`
- Optional `acceptable_evidence` type `qec_external_certificate` (future promotion gate)
- CI job hook for reproducible prover versions (documented in roadmap; no yaml change required locally)

## Scalable checker design (`tools/qspecbench/qec_external.py`)

Future prover adapters will return certificates validated by:

1. JSON Schema (`qec_external_certificate.schema.json`)
2. `validate_qec_external_certificate()` semantic rules (this module)
3. Track-specific `qec_claim_scope` promotion rules in `validate.py`
4. Explicit `trust_boundary.assumptions_not_checked` — no silent `reference_claim`

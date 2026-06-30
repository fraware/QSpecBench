# Governance

QSpecBench uses three maintainer roles. Initial maintainership is open to community volunteers via issue discussion.

## Schema maintainers

Responsible for schema design, validation rules, and compatibility.

**Invitation process:** open a discussion or comment on a schema-change issue; schema maintainers confirm by track record of merged schema PRs.

## Track maintainers

Responsible for algorithms, equivalence, QEC, Hamiltonian, and AI-formalization tracks.

| Track | Scope |
|-------|--------|
| Algorithms | Protocol and circuit correctness claims |
| Equivalence | Unitary and compiler equivalence |
| QEC | Codes, decoders, correction (honest trust boundaries) |
| Hamiltonian | Simulation, mappings, resource contracts |
| AI formalization | Draft formalization and semantic rubric |

**Invitation process:** propose yourself on a track-related PR or benchmark issue; existing contributors nominate in review.

## Evidence maintainers

Responsible for adapters, checker integration, trust-level rules, and CI behavior (Lean, QCEC, SMT, certificates).

## Review policy

Every benchmark PR is reviewed across:

1. **Scientific review** â€” claim sense, assumptions, terminology
2. **Specification review** â€” spec matches informal claim, semantics clear
3. **Evidence review** â€” evidence supports claim, checker declared, trust honest

No maintainer should merge their own reference-level benchmark without review.

### Dual review for `reference_claim`

Promoting a benchmark to `reference_claim` requires two recorded reviews in `spec.yaml`:

```yaml
status:
  reviews:
    formal_evidence_review:
      status: approved   # or required during bootstrap
      reviewer: <handle>
      date: YYYY-MM-DD
    domain_semantics_review:
      status: approved
      reviewer: <handle>
      date: YYYY-MM-DD
```

- **Formal evidence review** â€” Lean/kernel proofs, bridge manifests, checker output, obligation mapping
- **Domain semantics review** â€” Claim wording, assumptions, `checked_under` / `not_checked_under` scope

`qspecbench validate` rejects `reference_claim` without both reviews at `approved` or `required` status.
Bootstrap corpus entries may use `maintainer-bootstrap` with documented notes; new promotions must use real reviewers.


### AI-formalization track

Benchmarks on the `ai_formalization` track promoted to `reference_claim` require **named reviewer identity**
in both review blocks before the headline claim is considered governance-complete:

- `status.reviews.formal_evidence_review.reviewer` — non-empty, not `maintainer-bootstrap`
- `status.reviews.domain_semantics_review.reviewer` — non-empty, not `maintainer-bootstrap`

`qspecbench validate` **hard-fails** `reference_claim` on the `ai_formalization` track when either
review block lacks a named non-bootstrap reviewer. Enforcement effective from corpus **v0.2.2**
(tag `e5ee749`). Optional `review_artifact_sha256` on review blocks records signed review bundles.

### Coq / Rocq / Isabelle second-assistant track

Coq (and Rocq/Isabelle stub adapters) are **excluded from default maturity and dashboard counts**
until an optional CI job runs with `QSPECBENCH_COQ=1` and a working `coqc` on `PATH`. Lean 4 remains
the only kernel-checked proof assistant in the default CI gate. Coq smoke files (for example
`cnot_coq_smoke.v`) document the intended second-assistant path but do not affect maturity tiers.


## Reference-claim promotion

Reference levels are scoped (see [docs/reference_benchmarks.md](docs/reference_benchmarks.md)). A
benchmark is promoted to `reference_claim` only when its `claim_scope` / `proved_scope` obligations are
all checked and `headline_claim_status` is `checked`.

QEC-specific: a correction claim (for example, "corrects any single X error") requires **checked
correction evidence** for `reference_claim`. An assumed decoder/lookup table supports at most
`reference_scaffold` / `reference_artifact`, and the correction obligation must remain in
`proved_scope.unproved_obligations`.


### `artifact_bound_reference_claim` (reserved tier — schema only)

This maturity tier is defined in schema v0.2. Six kernel-bridge pilots are promoted at **v0.2.3**
(`49e8899`): `cnot_self_inverse_cancellation`, `bell_state_preparation`, `hadamard_conjugates_x_to_z`,
`single_qubit_gate_cancellation`, `swap_from_three_cx`, and source-side `toffoli_decomposition_equivalence`.
Do not set `status.maturity: artifact_bound_reference_claim` without meeting every requirement;
`qspecbench validate` fails closed (including `qspecbench bridge-metadata verify` for BridgeMetadata pins).

**Promotion checklist (all required):**

1. Dual review — both `formal_evidence_review` and `domain_semantics_review` at `approved` with named non-bootstrap reviewers
2. `headline_claim_status.status: checked` with honest `checked_under` / `not_checked_under`
3. `proved_scope.unproved_obligations` empty
4. `semantic_bridge.claimed_link: kernel_checked_codegen_trace` or `kernel_checked_artifact_semantics` with anchors:
   - `artifact_sha256`, `gate_trace_sha256`, `lean_ast_sha256`, `ast_authority: lean_mirror`, `generated_lean_sha256`
   - `theorem_identifier_sha256`, `theorem_elaborator_hash`, `theorem_source_statement_hash` (secondary when elaborator cache present)
5. Passing `bridge_verify` evidence and matching Lean `BridgeMetadata` pins (manifest-sourced hashes)
6. README claim card documents artifact hash binding and checker chain

## Schema changes

Breaking schema changes require a version bump and migration notes in `docs/schema_migration_*.md`.

## Artifact schema deadlines

- **Hamiltonian JSON:** legacy artifacts without top-level `type` were rejected starting corpus **v0.2.0** tooling gate (migration completed in v0.1.x). All Hamiltonian artifacts must validate against `schema/hamiltonian.schema.json` (see `docs/versioning.md`).

Schema changes must be versioned, documented, and justified by real benchmark needs. Schema, tooling,
and corpus are versioned separately; see [docs/versioning.md](docs/versioning.md).

**Current release:** tag `v0.2.3` (commit `49e8899`); six `artifact_bound_reference_claim` kernel bridges; six `kernel_checked_artifact_semantics` bridges with Lean parse→codegen chain and `ast_authority: lean_mirror`. CI: [validate workflow](https://github.com/fraware/QSpecBench/actions/workflows/validate.yml) on `main`.

# Governance

QSpecBench uses named maintainer **roles**. Only real GitHub handles appear in
[`.github/CODEOWNERS`](.github/CODEOWNERS). Until additional maintainers are
invited, `@fraware` is the **interim sole owner** on every CODEOWNERS path;
role names below are the assignment targets (do not invent fake GitHub users).

Initial maintainership beyond the interim owner is open to community volunteers
via issue discussion.

## Maintainer assignment

| Role ID | Scope (CODEOWNERS paths) | GitHub handle | Status |
|---------|--------------------------|---------------|--------|
| `schema-maintainer` | `/schema/**`, default `*` | `@fraware` | Assigned (interim sole owner) |
| `tooling-trust-maintainer` | `reviews.py`, `trust.py`, `claim_coherence.py`, default `*` | `@fraware` | Assigned (interim sole owner) |
| `lean-evidence-maintainer` | `/lean/**`, `/adapters/**` | *to be assigned* | Vacant — interim `@fraware` |
| `algorithms-track-maintainer` | `/benchmarks/algorithms/**` | *to be assigned* | Vacant — interim `@fraware` |
| `equivalence-track-maintainer` | `/benchmarks/equivalence/**` | *to be assigned* | Vacant — interim `@fraware` |
| `qec-track-maintainer` | `/benchmarks/qec/**` | *to be assigned* | Vacant — interim `@fraware` |
| `hamiltonian-track-maintainer` | `/benchmarks/hamiltonian/**` | *to be assigned* | Vacant — interim `@fraware` |
| `ai-formalization-track-maintainer` | `/benchmarks/ai_formalization/**` | *to be assigned* | Vacant — interim `@fraware` |

When a role is filled: (1) update this table with the real handle, (2) replace the
interim `@fraware` entry for that path in `.github/CODEOWNERS`, (3) invite the
assignee as a repo collaborator with review rights.

### How to assign a track maintainer

Track roles (`algorithms-track-maintainer`, `equivalence-track-maintainer`,
`qec-track-maintainer`, `hamiltonian-track-maintainer`,
`ai-formalization-track-maintainer`) and `lean-evidence-maintainer` stay
**vacant / TBA** until a real person volunteers. Do **not** invent GitHub handles
or placeholder users.

1. **Nominate** — Candidate proposes on a track-related issue/PR, or an existing
   contributor nominates them in review. Interim owner `@fraware` confirms scope.
2. **Record the real handle** — Replace `*to be assigned*` in the table above with
   the assignee’s actual `@github-handle` and set Status to `Assigned`.
3. **Update CODEOWNERS** — For that track path only, replace the interim
   `@fraware` line with the real handle in [`.github/CODEOWNERS`](.github/CODEOWNERS).
   Leave other vacant paths on interim `@fraware`.
4. **Invite** — Add the assignee as a repo collaborator with review rights; they
   acknowledge dual-review / no self-merge rules in this document.
5. **Do not** invent handles for empty seats, bulk-file `QSB-AUD-*` GitHub issues,
   or mark community DoD boxes “filled” with fake names.

Until steps 2–4 complete for a role, public language remains: vacancies explicit TBA,
interim sole owner `@fraware` on every CODEOWNERS path.

## Schema maintainers

Responsible for schema design, validation rules, and compatibility.
Role ID: `schema-maintainer`.

**Invitation process:** open a discussion or comment on a schema-change issue; schema maintainers confirm by track record of merged schema PRs.

## Track maintainers

Responsible for algorithms, equivalence, QEC, Hamiltonian, and AI-formalization tracks.

| Track | Role ID | Scope |
|-------|---------|--------|
| Algorithms | `algorithms-track-maintainer` | Protocol and circuit correctness claims |
| Equivalence | `equivalence-track-maintainer` | Unitary and compiler equivalence |
| QEC | `qec-track-maintainer` | Codes, decoders, correction (honest trust boundaries) |
| Hamiltonian | `hamiltonian-track-maintainer` | Simulation, mappings, resource contracts |
| AI formalization | `ai-formalization-track-maintainer` | Draft formalization and semantic rubric |

**Invitation process:** propose yourself on a track-related PR or benchmark issue;
existing contributors nominate in review. Filling the role follows
[How to assign a track maintainer](#how-to-assign-a-track-maintainer) above —
vacancies stay TBA until a real handle is recorded.

## Evidence maintainers

Responsible for adapters, checker integration, trust-level rules, and CI behavior (Lean, QCEC, SMT, certificates).
Role ID: `lean-evidence-maintainer` (Lean + adapters) together with `tooling-trust-maintainer` (promotion/review gates).

## Review policy

Every benchmark PR is reviewed across:

1. **Scientific review** — claim sense, assumptions, terminology
2. **Specification review** — spec matches informal claim, semantics clear
3. **Evidence review** — evidence supports claim, checker declared, trust honest

No maintainer should merge their own reference-level benchmark without review.
Author and merging maintainer are barred from both promotion review seats.

### Dual review for `reference_claim` / ABRC

Promoting a benchmark to `reference_claim` or `artifact_bound_reference_claim`
requires two **approved** reviews with hash-bound review artifacts:

```yaml
status:
  reviews:
    formal_evidence_review:
      status: approved
      reviewer: <stable-named-identity>
      date: YYYY-MM-DD
      review_artifact_path: reviews/formal_review.json
      review_artifact_sha256: <sha256>
      review_commit: <git-sha>
    domain_semantics_review:
      status: approved
      reviewer: <different-stable-named-identity>
      date: YYYY-MM-DD
      review_artifact_path: reviews/domain_review.json
      review_artifact_sha256: <sha256>
      review_commit: <git-sha>
```

- **Formal evidence review** — Lean/kernel proofs, bridge manifests, checker output, obligation mapping
- **Domain semantics review** — Claim wording, assumptions, `checked_under` / `not_checked_under` scope

`qspecbench validate` rejects checked headlines unless both reviews are `approved`
(not `required`), reviewers are distinct and non-bootstrap, author ≠ either
reviewer, merger ≠ either reviewer, and review artifacts validate against
`schema/review_artifact.schema.json`.

Code ownership for trust-critical paths is declared in `.github/CODEOWNERS`
(role map + interim sole owner; see Maintainer assignment above).
Audit backlog is tracked in [`docs/audit_issues.yaml`](docs/audit_issues.yaml)
(markdown summarizes). Open/partial findings use stable stub IDs in
[`docs/audit_github_issues.yaml`](docs/audit_github_issues.yaml); remote GitHub
Issues are filed only when a maintainer picks up a finding (do not bulk-create).


### AI-formalization track

Benchmarks on the `ai_formalization` track promoted to `reference_claim` require **named reviewer identity**
in both review blocks before the headline claim is considered governance-complete:

- `status.reviews.formal_evidence_review.reviewer` — non-empty, not `maintainer-bootstrap`
- `status.reviews.domain_semantics_review.reviewer` — non-empty, not `maintainer-bootstrap`

`qspecbench validate` **hard-fails** `reference_claim` on the `ai_formalization` track when either
review block lacks a named non-bootstrap reviewer. Enforcement effective from corpus **v0.2.2**
(tag `e5ee749`). Required `review_artifact_sha256` on promotion review blocks pin hash-bound
review JSON; see signed-review residual below.

### Second-kernel policy (Lean-primary)

**Decision (Phase E):** Lean 4 is the **only** proof assistant in the default CI maturity
gate. Coq, Rocq, and Isabelle remain **discovery / opt-in** — never required for
`reference_claim` / ABRC promotion, dashboard maturity counts, or default
[`.github/workflows/validate.yml`](.github/workflows/validate.yml) green.

| Assistant | Default CI | Maturity / dashboard | Path |
|-----------|------------|----------------------|------|
| Lean 4 | Required (`lake build`) | Counted | `lean/`, `lean_proof` evidence |
| Coq | Opt-in (`QSPECBENCH_COQ=1`, `coqc` on `PATH`) | Excluded | `adapters/coq/` |
| Rocq / Isabelle | Stub / skip only | Excluded; permanent non-checked | discovery stubs |

Rationale: shipping a second kernel in default CI would imply checked dual-assistant
coverage the corpus does not have. Discovery adapters and smoke files (for example
`cnot_coq_smoke.v`) document the intended path without affecting trust tiers.
See also [docs/definition_of_completion.md](docs/definition_of_completion.md)
permanent residuals.

### Signed review residual (optional)

Promotion requires **hash-bound** review artifacts (`review_artifact_path` /
`review_artifact_sha256` / `review_commit`) validating against
`schema/review_artifact.schema.json`. Cryptographic signatures on the optional
`signature` field (GPG, cosign, or similar) are **not** required in schema 0.3 —
unsigned corpus pins via SHA-256 remain the trust surface. Signed reviews are a
documented Phase 9 residual for a future schema/tooling bump.


## Reference-claim promotion

Reference levels are scoped (see [docs/reference_benchmarks.md](docs/reference_benchmarks.md)). A
benchmark is promoted to `reference_claim` only when its `claim_scope` / `proved_scope` obligations are
all checked and `headline_claim_status` is `checked`.

QEC-specific: a correction claim (for example, "corrects any single X error") requires **checked
correction evidence** for `reference_claim`. An assumed decoder/lookup table supports at most
`reference_scaffold` / `reference_artifact`, and the correction obligation must remain in
`proved_scope.unproved_obligations`.


### `artifact_bound_reference_claim` (ABRC)

This maturity tier is defined in schema v0.2+. Tag **v0.2.3** (`49e8899`) shipped the first six
kernel-bridge ABRC pilots. The **live corpus** (see [docs/status.md](docs/status.md)) currently has
**ten** ABRC benchmarks:

| Benchmark | Track | Claimed link / scope note |
|-----------|-------|---------------------------|
| `cnot_self_inverse_cancellation` | equivalence | `kernel_checked_codegen_trace` / artifact semantics |
| `hadamard_conjugates_x_to_z` | equivalence | codegen-trace bridge |
| `single_qubit_gate_cancellation` | equivalence | codegen-trace bridge |
| `clifford_simplification_preserves_unitary` | equivalence | normalized Clifford source vs. target denotation (`denotateOps1C_normalized`) |
| `native_ccx_artifact_denotes_toffoli_unitary` | equivalence | native CCX artifact denotation only |
| `toffoli_decomposition_equivalence` | equivalence | **normalized** Clifford+T denotation (`denotateOps3C_normalized`); unnormalized pair equality out of scope |
| `bell_state_preparation` | algorithms | codegen-trace bridge |
| `swap_from_three_cx` | algorithms | source–target exact denotation |
| `teleportation_preserves_state_up_to_pauli_correction` | algorithms | unitary-prefix proposition v2 (not full dynamic matrix KERNEL_BRIDGE) |
| `teleportation_dynamic_feedforward_protocol` | algorithms | sibling ABRC via `kernel_checked_dynamic_denotation` (promoted from `kernel_checked_dynamic_ast_semantics`) |

Do not set `status.maturity: artifact_bound_reference_claim` without meeting every requirement;
`qspecbench validate` fails closed (including `qspecbench bridge-metadata verify` for BridgeMetadata pins).

**Promotion checklist (all required):**

1. Dual review — both `formal_evidence_review` and `domain_semantics_review` at `approved` with named non-bootstrap reviewers
2. `headline_claim_status.status: checked` with honest `checked_under` / `not_checked_under`
3. `proved_scope.unproved_obligations` empty
4. `semantic_bridge.claimed_link` one of:
   - `kernel_checked_codegen_trace` or `kernel_checked_artifact_semantics` with anchors:
     `artifact_sha256`, `gate_trace_sha256`, `lean_ast_sha256`, `ast_authority: lean_mirror`, `generated_lean_sha256`,
     `theorem_identifier_sha256`, `theorem_elaborator_hash`, `theorem_source_statement_hash`
   - **or** `kernel_checked_dynamic_ast_semantics` (measure+if CanonicalAst+protocol ABRC) with anchors:
     `dynamic_artifact_sha256`, `dynamic_ast_sha256`, fail-closed mirror verify (`dynamic_ast_match: true`,
     `matrix_match: false`), and Lean `DynamicAstBridgeMetadata` pin — **never** matrix KERNEL_BRIDGE for dynamics
5. Passing bridge verify evidence (`bridge_verify` or `dynamic_ast_bridge_verify`) and matching Lean metadata pins
6. README claim card documents artifact hash binding and checker chain

## Schema changes

Breaking schema changes require a version bump and migration notes in `docs/schema_migration_*.md`.

## Artifact schema deadlines

- **Hamiltonian JSON:** legacy artifacts without top-level `type` were rejected starting corpus **v0.2.0** tooling gate (migration completed in v0.1.x). All Hamiltonian artifacts must validate against `schema/hamiltonian.schema.json` (see `docs/versioning.md`).

Schema changes must be versioned, documented, and justified by real benchmark needs. Schema, tooling,
and corpus are versioned separately; see [docs/versioning.md](docs/versioning.md).

**Tagged release:** `v0.2.3` (commit `49e8899`) — first six ABRC kernel bridges + elaborator/AST authority (schema 0.3).
**Working tree (post-tag):** regenerate [docs/status.md](docs/status.md) for live counts (currently **10** ABRC, **9** `reference_claim`); see latest git tag / release notes when cutting the next corpus tag. CI: [validate workflow](https://github.com/fraware/QSpecBench/actions/workflows/validate.yml) on `main`.

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

1. **Scientific review** — claim sense, assumptions, terminology
2. **Specification review** — spec matches informal claim, semantics clear
3. **Evidence review** — evidence supports claim, checker declared, trust honest

No maintainer should merge their own reference-level benchmark without review.

## Reference-claim promotion

Reference levels are scoped (see [docs/reference_benchmarks.md](docs/reference_benchmarks.md)). A
benchmark is promoted to `reference_claim` only when its `claim_scope` / `proved_scope` obligations are
all checked and `headline_claim_status` is `checked`.

QEC-specific: a correction claim (for example, "corrects any single X error") requires **checked
correction evidence** for `reference_claim`. An assumed decoder/lookup table supports at most
`reference_scaffold` / `reference_artifact`, and the correction obligation must remain in
`proved_scope.unproved_obligations`.

## Schema changes

Schema changes must be versioned, documented, and justified by real benchmark needs. Schema, tooling,
and corpus are versioned separately; see [docs/versioning.md](docs/versioning.md).

# Release-engineering ledger

This file records immutable identities used by the v1 completion path. It is not a substitute for a signed release manifest.

## Archival freeze

| Field | Value |
|---|---|
| Archival tag | `archive/full-vision-f22f406` |
| Frozen SHA | `f22f406386bf27cbe7b4dbbc83b99951205f3018` |
| Source branch | `origin/phase4-native-proof-trust` |
| Draft PR | [#11](https://github.com/fraware/QSpecBench/pull/11) (integration source, not the merge vehicle) |
| Successor branch | `v1-completion` created from the frozen SHA; not rebased onto `main` |
| Local `main` at freeze | `54ad8d1003600068b9003a7697454858321abb9c` |

Exact-head CI on the frozen SHA: Validate / Promotion Check / Lint were green; Lean-QEC was failing. That failure is a reproduction outcome, not a theorem disproof, and must not be deleted, skipped, or simulated green.

## Promotion freeze

New `reference_claim` and `artifact_bound_reference_claim` promotions are blocked until authentic independent reviewer identities exist. v1 ships with those labels unreachable. See `docs/promotion_freeze.md`.

## Out of scope

Issue #9 (independent third-party cold-host reproduction) remains `post-v1`. Internal clean-environment verification must not be labeled external reproduction.

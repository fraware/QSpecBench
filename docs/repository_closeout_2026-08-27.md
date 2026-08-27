# Repository closeout — 27 August 2026

This document records the repository-hygiene closeout of the August 2026 QSpecBench implementation pass. It is deliberately narrower than a `v1.0.0` release declaration. Repository cleanup, engineering integration, community-grade governance, scientific reference-suite completion, and immutable release readiness are different claims and must not be conflated.

## Integration disposition

PR #32, **Make semantic profiles executable, versioned, and cross-consistent**, was squash-merged to `main` after exact-head Lint, Promotion Check, and the full Validate matrix succeeded. It closes issue #14. The merge preserves historical semantic interpreters and adds new versioned v2 profiles rather than silently reinterpreting old evidence.

The earlier August integration lines are already represented on `main` or were explicitly superseded by their successor PRs:

- v1 completion and full-vision substrate: merged through PRs #11 and #24;
- evidence-adapter repair: merged through PR #25;
- typed-adapter dispatch predecessor: PR #26 closed as superseded; its intended work was folded into PR #30;
- Lean-QEC provenance predecessor: PR #27 closed as superseded by the exact-head successor; final repair merged through PR #29;
- pytest configuration cleanup: merged through PR #28;
- typed adapter protocol migration: merged through PR #30, closing issue #15;
- non-vacuous v1 release contract: merged through PR #31;
- executable semantic-profile authority: merged through PR #32, closing issue #14.

Older compiler staging, phase, tier-gap, wave-3, QEC-fix, temporary, and v1-completion branches were audited against `main`. They either had no unique commits relative to `main` or represented historical/superseded commit ancestry whose substantive successor PR is already merged.

## Branch-closeout invariant

The desired operational state is one source of truth: `main`.

The connected GitHub mutation surface used for this closeout does not expose deletion of Git refs. Therefore branch names cannot be literally removed through this execution path. To eliminate divergent active state without claiming a deletion that did not occur, every non-`main` branch ref is repointed to the exact verified commit containing this closeout record. After that operation, the surviving branch names are inert aliases of `main`: they contain no unique repository state and must not be treated as active development branches.

If branch deletion is later performed through GitHub's UI or another authorized API surface, it is pure namespace cleanup; no code integration should be required.

## Pull-request closeout invariant

At completion of this closeout there must be zero open pull requests. Historical PRs remain in GitHub as the audit trail of what was merged, superseded, or intentionally closed. Closed/superseded PRs are not reopened merely to make commit ancestry visually linear.

## Issues intentionally left open

Repository hygiene does **not** justify closing an issue whose exit criteria are not met. In particular, the following classes remain real work and are intentionally preserved as open issues where applicable:

- authenticated independent reviewers and anti-self-promotion governance (#12, #19);
- non-vacuous release-corpus assurance-graph closure (#13);
- AI formalization semantic adjudication (#16);
- stronger scientific flagship results (#17);
- broader QEC/interoperability work (#18, #22);
- exact release-candidate evidence and immutable release packaging (#20, #23);
- generated/public documentation derivation work not yet proven complete (#21);
- standing contribution, independent-reproduction, and future-release audit tasks (#8–#10).

Issue #14 is closed by PR #32. Issue #15 was closed by PR #30. Their completion must not be used to imply completion of the independent governance, scientific, assurance-corpus, or release obligations above.

## Governance state

Live repository inspection during this closeout reports `main` as unprotected (`protected: false`). That is a concrete unmet governance condition, not an unknown. Issue #19 therefore remains open. The repository must not be described as community-grade until the required protection, independent ownership/review, and anti-self-promotion controls are actually enabled and evidenced.

## Release state

The v1 release decision remains **revise**, as defined in `docs/release_audit_v1.md`.

In particular:

- the canonical release contract intentionally requires a non-empty assurance corpus and non-vacuous qualification;
- the five Level-C reference capability assignments are not satisfied merely because machine-closed experimental packages exist;
- the promoted reference/gold inventory remains empty unless and until genuine reference maturity and independent-review requirements are met;
- a green development or closeout commit is not an immutable `v1.0.0` release;
- release SBOM, provenance/archive, governance, scientific-reference-suite, and strict candidate qualification requirements remain governed by their existing open issues and release documents.

No tag or release should be created from this closeout merely because repository integration is clean.

## Exact-head completion condition

This repository-hygiene closeout is operationally complete only when all of the following are true for the exact `main` commit containing this file:

1. push-triggered Validate is terminal and successful, including Lean build, `QSpecBench.Evidence.All`, corpus validation/check-evidence, bridge verification, unit/trust tests, Stim tests, dashboard drift, and release-bundle smoke;
2. push-triggered Lint is terminal and successful;
3. push-triggered Promotion Check is terminal and successful;
4. Dashboard is terminal and successful;
5. there are zero open PRs;
6. every surviving non-`main` branch ref points to that exact verified `main` commit.

This condition is intentionally exact-SHA based. Evidence from a PR head or predecessor SHA is not transferred to a later `main` commit.

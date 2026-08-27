# QSpecBench full-vision execution gates

This document turns the project vision into auditable exit conditions. It deliberately separates repository engineering from scientific and governance claims so that completion cannot be declared by changing labels.

The machine-readable v1 qualification contract is [`release_v1_contract.yaml`](release_v1_contract.yaml), validated against `schema/release_contract.schema.json`. This document explains the scientific and engineering intent; the contract defines the non-vacuous release-corpus selectors and Level-C reference-capability assignments used by release qualification.

## Governing invariant

Every promoted maturity label must allow a reader to determine exactly:

1. which proposition was checked;
2. against which concrete artifact(s);
3. under which semantic profile;
4. which obligations define the proposition;
5. which evidence discharges each obligation;
6. which checker/proof/tool produced that evidence;
7. which human reviewers approved the evidence and semantics;
8. which assumptions and trust boundaries remain.

A stronger checker does not repair a weaker proposition. A kernel-checked theorem does not imply that the theorem is semantically equivalent to the intended scientific claim. A finite simulation does not imply a universal theorem. A distance certificate does not imply an end-to-end QEC protocol. An entry-wise numerical bound does not imply an operator-level simulation guarantee.

## Four distinct completion levels

### A. Engineering release-ready

Required:
- exact-SHA CI is green;
- schema/layout/trust/assurance validation passes;
- all declared evidence is reproducible under pinned tool versions;
- release bundle is built from the exact commit and verifies after unpacking;
- theorem exports, semantic profiles, adapter identities, artifact hashes and review artifacts are included;
- generated status documentation has no drift;
- security/resource limits remain fail-closed.

Engineering substrate milestones already merged include the typed adapter execution/trust boundary (#30/#15), the non-vacuous release-contract foundation (#31), and executable/cross-consistent semantic-profile authority (#32/#14). These implemented mechanisms do not by themselves satisfy release-corpus closure, governance, scientific reference maturity, or immutable-release requirements.

### B. Community-grade governance

Required:
- real, verifiable maintainers/reviewers exist beyond the author/merger;
- branch protection and required checks are enabled;
- trust-critical CODEOWNERS rules are enforced;
- promoted claims cannot be self-reviewed or self-promoted;
- review attestations bind durable reviewer identity, reviewed commit, artifact hashes, accepted obligations, conflicts and public review event;
- open audit findings are represented by real public issues.

The current interim sole-owner state does **not** satisfy this level. Live repository inspection on 27 Aug 2026 also reports `main` as unprotected (`protected: false`), so issue #19 is a concrete unmet governance gate rather than an unknown.

### C. Scientific reference suite

Required flagships:
- a real compiler-generated source→target transformation with artifact-bound exact equivalence;
- an arbitrary-input dynamic protocol with formal measurement/classical-feed-forward semantics;
- a QEC chain that keeps family/code validity, distance, syndrome extraction, decoder contract, correction relation and repeated rounds distinct;
- an operator-level Hamiltonian product-formula approximation theorem under explicit finite-dimensional hypotheses;
- an AI formalization benchmark whose semantic relation to the source claim is externally adjudicated and cannot receive an equivalence score for a strict weakening.

These five requirements correspond one-to-one to the five required capabilities in `docs/release_v1_contract.yaml`. A capability is not satisfied by naming a benchmark: strict qualification additionally requires the assigned package to be in the release corpus, have reference maturity, and satisfy the configured independent-review policy.

### D. Full vision

Required:
- proposition identity and relation are first-class and versioned;
- semantic profiles are executable, versioned, standard-pinned and cross-consistent;
- proof obligations form a typed graph;
- every required obligation has explicit supporting evidence edges;
- adapter inputs/results are typed, hash-bound and versioned;
- maturity is derived from graph closure rather than manually authored status;
- heterogeneous proof/checker ecosystems interoperate without collapsing their trust boundaries;
- releases are immutable, citable and independently auditable.

The external reproduction program is intentionally excluded from the current execution request; nothing in this document silently marks that excluded activity complete.

## Current migration policy

`assurance_graph.yaml` is the additive migration surface toward schema v0.4. Legacy schema-0.3 promoted claims receive a validator warning when the sidecar is absent. Once a sidecar exists, it is fail-closed: every required obligation must be represented and supported by explicit passing evidence, proposition identity must match, and semantic-profile contradictions fail validation.

For v1 qualification, assurance migration is evaluated over the **release corpus**, not merely the promoted-reference set. The canonical contract currently selects `experimental_closed`, `reference_claim`, and `artifact_bound_reference_claim` packages, plus any explicit contract overrides. The selector is required to be non-empty. Consequently, zero reference claims can never make graph migration vacuously complete.

The release-corpus graph migration is not complete until every selected package has a closed graph. Reference-suite packages then face the additional reference-maturity and authenticated independent-review requirements. Existing authored `status.ci`, `status.evidence`, `proved_scope.checked_obligations`, and maturity fields remain descriptive legacy fields until derived-state migration is complete.

Semantic-profile authority is no longer part of this remaining migration: PR #32 closed #14 with immutable historical profiles plus strict executable static/dynamic v2 profiles, explicit grammar/numeric semantics, and profile/bridge consistency checks. Typed adapter execution identity is likewise merged through PR #30/#15. The principal current graph/qualification migration is issue #13.

## Promotion freeze

Until reviewer authentication and release-corpus assurance-graph migration are complete, new `reference_claim` and `artifact_bound_reference_claim` promotions should be treated as blocked. Lower maturities may continue for research scaffolds if their limitations are explicit.

## Dependency order

1. exact-head release baseline and CI evidence;
2. typed adapter execution/trust boundary — **migration merged in #30; preserve by conformance testing**;
3. canonical non-vacuous release contract and release-corpus assurance migration — **contract foundation merged in #31; corpus closure remains #13**;
4. executable semantic profiles — **implemented and merged in #32; issue #14 closed**;
5. three scientific flagships: compiler equivalence, dynamic protocol, Hamiltonian approximation;
6. QEC external-certificate interoperability and family assurance;
7. AI formalization relation/metric rebuild;
8. reviewer authentication and governance gates before any reference promotion;
9. version-isolated ecosystem interoperability and canonical release-gate convergence;
10. immutable citable release packaging.

Some research and governance work may proceed in parallel, but no downstream phase may be used rhetorically to claim an upstream phase is complete.

## Repository-closeout boundary

Repository integration hygiene is documented in [repository_closeout_2026-08-27.md](repository_closeout_2026-08-27.md). That closeout is allowed to establish a single integrated code state on `main`; it is not allowed to weaken the open exit criteria in Levels B–D or to relabel the v1 audit from `revise` to `ship`.

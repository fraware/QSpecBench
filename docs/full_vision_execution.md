# QSpecBench full-vision execution gates

This document turns the project vision into auditable exit conditions. It deliberately separates repository engineering from scientific and governance claims so that completion cannot be declared by changing labels.

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

### B. Community-grade governance

Required:
- real, verifiable maintainers/reviewers exist beyond the author/merger;
- branch protection and required checks are enabled;
- trust-critical CODEOWNERS rules are enforced;
- promoted claims cannot be self-reviewed or self-promoted;
- review attestations bind durable reviewer identity, reviewed commit, artifact hashes, accepted obligations, conflicts and public review event;
- open audit findings are represented by real public issues.

The current interim sole-owner state does **not** satisfy this level.

### C. Scientific reference suite

Required flagships:
- a real compiler-generated source→target transformation with artifact-bound exact equivalence;
- an arbitrary-input dynamic protocol with formal measurement/classical-feed-forward semantics;
- a QEC chain that keeps family/code validity, distance, syndrome extraction, decoder contract, correction relation and repeated rounds distinct;
- an operator-level Hamiltonian product-formula approximation theorem under explicit finite-dimensional hypotheses;
- an AI formalization benchmark whose semantic relation to the source claim is externally adjudicated and cannot receive an equivalence score for a strict weakening.

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

The migration is not complete until every promoted claim has a closed graph and authenticated reviews. Existing authored `status.ci`, `status.evidence`, `proved_scope.checked_obligations`, and maturity fields remain descriptive legacy fields until derived-state migration is complete.

## Promotion freeze

Until reviewer authentication and corpus-wide assurance-graph migration are complete, new `reference_claim` and `artifact_bound_reference_claim` promotions should be treated as blocked. Lower maturities may continue for research scaffolds if their limitations are explicit.

## Dependency order

1. exact-head release baseline and CI evidence;
2. reviewer authentication and governance gates;
3. corpus-wide proposition/obligation/evidence graph migration;
4. executable semantic profiles;
5. typed adapter migration;
6. three scientific flagships: compiler equivalence, dynamic protocol, Hamiltonian approximation;
7. QEC external-certificate interoperability and family assurance;
8. AI formalization relation/metric rebuild;
9. version-isolated ecosystem interoperability;
10. immutable citable release packaging.

No downstream phase may be used rhetorically to claim an upstream phase is complete.

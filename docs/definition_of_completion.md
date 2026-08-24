# Definition of completion

QSpecBench must not use one checklist to collapse engineering readiness, governance independence, scientific depth, and the long-term full vision. These are different claims and have different evidence requirements.

Until the relevant level below is actually satisfied, public language should remain scoped. A passing theorem, a valid schema, or a populated CODEOWNERS file cannot substitute for independent review or scientific adequacy.

Regenerate live corpus counts with:

```bash
qspecbench dashboard benchmarks/ --out docs/status.md
```

The dependency-ordered full-vision gates are documented in [full_vision_execution.md](full_vision_execution.md).

---

## Level A — engineering release-ready

| # | Criterion | How verified | Current status |
|---|-----------|--------------|----------------|
| A1 | Schema/layout/trust validation passes on exact release commit | `.github/workflows/validate.yml` | Implemented gate; exact current PR/head result must be verified before merge/release |
| A2 | Lean evidence aggregate builds on exact release commit | `lake build QSpecBench.Evidence.All` in CI | Implemented gate; exact current PR/head result must be verified |
| A3 | Evidence checks execute under pinned dependencies and fail closed | `qspecbench check-evidence`, lockfiles/workflows | Implemented machinery; exact current PR/head result must be verified |
| A4 | Release bundle is built from and verifies against the exact commit | `.github/workflows/release.yml`, release-bundle verifier | Implemented machinery; no new release is claimed merely by editing metadata |
| A5 | Promotion state is derivable from explicit obligation→evidence closure | `assurance_graph.yaml` + validator | **In migration** — PR #11 establishes the contract/pilot; issue #13 tracks corpus-wide migration |
| A6 | Semantic profile is authoritative and cross-consistent | registered profiles + assurance validator | **In migration** — issue #14 |
| A7 | Adapter results bind proposition/semantics/input hashes/obligations | typed AdapterRequest/AdapterResult | **In migration** — issue #15 |
| A8 | Generated documentation cannot drift from corpus state | generated status/dashboard drift test | **In progress** |

Engineering readiness is not community-grade governance.

---

## Level B — community-grade governance

| # | Criterion | How verified | Current status |
|---|-----------|--------------|----------------|
| B1 | Real maintainers/reviewers exist beyond the author/merger | CODEOWNERS + public GitHub identities | **Not met** — current trust-critical ownership is interim `@fraware`; role vacancies remain TBA |
| B2 | Trust-critical branch protection and required code-owner review are enabled | GitHub repository settings | **Not independently verified / not claimed** |
| B3 | Promoted claims cannot be self-reviewed or self-promoted | governance rule + protected branch + validation | **Not met end-to-end** |
| B4 | Every promoted claim has two authenticated, independent review attestations | `review_attestation_v2` + public review event | **Not met** — legacy reviewer strings/hash-bound artifacts are not equivalent to authenticated identity; issue #12 |
| B5 | Open audit findings are represented by actual public GitHub issues | GitHub issues | **Partially met** — local `QSB-AUD-*` stubs alone do not satisfy this criterion |
| B6 | Contribution and second-kernel policies are explicit | CONTRIBUTING/GOVERNANCE/adapter docs | Met as documentation, but does not satisfy B1–B5 |

**QSpecBench must not currently be called community-grade on the basis of the old C1/C2 checklist.** Named role labels with a sole interim owner are not independent maintainers, and local audit IDs are not public issue tracking.

---

## Level C — scientific reference suite

The repository contains selected real checked claims, but the full scientific reference-suite target is stronger than the previous R1–R3 checklist.

| # | Criterion | Required scientific result | Current status |
|---|-----------|----------------------------|----------------|
| C1 | Real compiler transformation | Compiler/version/config-bound source→target artifacts with exact semantic equivalence and independent supporting checker | **Not yet met as flagship** — issue #17 |
| C2 | Full dynamic protocol | Arbitrary-input protocol with formal measurement/instrument, classical-register/feed-forward, and final subsystem correctness | **Not yet met as flagship** — current dynamic work is deliberately narrower; issue #17 |
| C3 | QEC assurance chain | Keep code/family validity, distance, syndrome extraction, decoder contract, correction/logical preservation and repeated rounds distinct; include non-toy certificate path | **Partially met** — small-code work is substantive; external/family integration issue #18 |
| C4 | Operator-level Hamiltonian approximation | Formally checked product-formula error in operator norm or stronger declared metric, meaningfully parameterized in time/step count | **Not yet met as flagship** — current entry-modulus/numerical proxies remain narrower; issue #17 |
| C5 | Semantically adjudicated AI formalization | Explicit source→formal relation; kernel-valid strict weakening cannot score as semantic equivalence | **Not yet met corpus-wide** — issue #16 |

Existing checked results should retain their exact scopes. This table does not demote valid narrow theorems; it prevents those theorems from being rhetorically expanded into stronger reference-suite claims.

---

## Level D — full vision

Required:

1. Proposition identity and proposition relations are first-class, immutable/versioned objects.
2. Semantic profiles are executable, standard-version-pinned, fail-closed, and cross-consistent with parsers/bridges/artifacts.
3. Required obligations form a typed graph.
4. Every required obligation has at least one explicit passing evidence edge with a declared trust class.
5. Adapter requests/results are typed and bind exact proposition, semantics, inputs, tool identity, scope, and outputs.
6. Maturity/checked scope is derived from graph closure, not manually asserted runtime fields.
7. Human review is authenticated and bound to exact propositions/artifacts/commits.
8. Heterogeneous proof/checker ecosystems interoperate without collapsing their trust boundaries.
9. Releases are immutable, citable and reproducible from exact commits, with theorem exports, lockfiles, attestations and archived bundles.
10. Scientific flagships satisfy Level C.

The external reproduction program is explicitly excluded from the current execution request and is not silently counted as completed here.

---

## Permanent residuals and scope discipline

The following principles are permanent even after Levels A–D improve:

- Device `hardware_semantics`, pulse schedules, and fidelity are not implied by a software ISA abstraction.
- A finite Stim/PyMatching declared universe is not all-code fault tolerance.
- A distance certificate is not syndrome-extraction-circuit correctness.
- A QCEC result is externally trusted supporting evidence unless its trust model is strengthened; it does not by itself define the semantic proposition.
- A kernel-checked theorem establishes the formal theorem under its assumptions, not the faithfulness of the theorem to a natural-language source claim.
- Entry-wise numerical error, finite sampling, or `N * epsilon` bookkeeping is not an operator-level Hamiltonian approximation theorem.
- QBricks/ZX/Coq/Rocq/Isabelle adapters or stubs are not badges of completeness; trust depends on the actual executed evidence path.
- Corpus-executed code uses constrained execution paths but is not a general sandbox product.

Never resolve a missing guarantee by renaming it into checked scope. Narrow the proposition or leave the obligation open.

---

## Live corpus snapshot

Source of truth remains the generated dashboard/status tooling. The audited Aug. 24, 2026 snapshot was:

- `artifact_bound_reference_claim`: 10
- `reference_claim`: 9
- total benchmarks excluding template: 50
- checked headlines: 19
- benchmarks with some checked evidence: 46

These counts are descriptive corpus state. They do **not** establish Level B community governance or Level C scientific-reference-suite completion.

Public implementation blockers and migration work are tracked in issues #12–#18 and draft PR #11.

# Definition of completion

QSpecBench must not use one checklist to collapse engineering readiness, governance independence, scientific depth, and the long-term full vision. These are different claims and have different evidence requirements.

Until the relevant level below is actually satisfied, public language should remain scoped. A passing theorem, a valid schema, or a populated CODEOWNERS file cannot substitute for independent review or scientific adequacy.

The canonical machine-readable v1 qualification policy is [release_v1_contract.yaml](release_v1_contract.yaml), under `schema/release_contract.schema.json`. It selects a non-empty release corpus independently of whether any benchmark has yet reached reference maturity and defines the five Level-C capability slots. Empty reference/gold inventory is therefore never interpreted as completion.

Regenerate live corpus counts with:

```bash
qspecbench dashboard benchmarks/ --out docs/status.md
python -c "from pathlib import Path; from qspecbench.generated_status import write_status_snapshot; write_status_snapshot(Path('benchmarks'), Path('docs/generated_status.md'))"
```

Structural release-contract validation during development:

```bash
python scripts/check_release_contract.py
```

Exact-head release verification (when cutting a candidate):

```bash
python scripts/release_verify.py --candidate-sha "$(git rev-parse HEAD)"
```

The release verifier invokes `scripts/check_release_contract.py --strict-qualification`, so it intentionally fails until every required Level-C capability is populated by a genuinely reference-qualified package and the selected release corpus has the required assurance sidecars.

The dependency-ordered full-vision gates are documented in [full_vision_execution.md](full_vision_execution.md).
v1 ship/revise decision: [release_audit_v1.md](release_audit_v1.md) (currently **revise**).

---

## Level A — engineering release-ready

| # | Criterion | How verified | Current status |
|---|-----------|--------------|----------------|
| A1 | Schema/layout/trust validation passes on exact release commit | `.github/workflows/validate.yml` | Implemented gate; exact current PR/head result must be verified before merge/release |
| A2 | Lean evidence aggregate builds on exact release commit | `lake build QSpecBench.Evidence.All` in CI | Implemented gate; exact current PR/head result must be verified |
| A3 | Evidence checks execute under pinned dependencies and fail closed | `qspecbench check-evidence`, lockfiles/workflows | Implemented machinery; exact current PR/head result must be verified |
| A4 | Release bundle is built from and verifies against the exact commit | `.github/workflows/release.yml`, release-bundle verifier | Implemented machinery; no new release is claimed merely by editing metadata |
| A5 | Promotion/release state is derivable from explicit obligation→evidence closure over a non-empty corpus | `release_v1_contract.yaml` + `assurance_graph.yaml` + validators | **In migration** — non-vacuous release contract established; issue #13 tracks release-corpus graph closure |
| A6 | Semantic profile is authoritative and cross-consistent | registered profiles + assurance validator | **In migration** — issue #14 |
| A7 | Adapter results bind proposition/semantics/input hashes/obligations through typed registered execution identities | typed AdapterRequest/AdapterResult + conformance tests | **Typed-adapter migration merged in #30**; exact-head conformance still required for every release candidate |
| A8 | Generated documentation cannot drift from corpus state | generated status/dashboard drift tests | Implemented for generated surfaces; regenerate before release |
| A9 | Lean-QEC cold native acceptance (distance-only adapter) | `QSPECBENCH_LEAN_QEC_VERIFY=1` structured result | **Demonstrated for the pinned BB90 state** — exact-head PR workflow at `cce598d94acdd368d77001e790eb0847353d914e` produced `ok=true`, `kernel_checked=true`, `acceptance.status=passing`, `kernel_typechecking_bypassed=false`, `upstream_default_reproduced=true`, and `fallback_used=false`; every release candidate must independently rerun and pass this lane at its own exact SHA |

Engineering readiness is not community-grade governance. Machine-closed `experimental_closed` packages do not satisfy gold/reference promotion.

---

## Level B — community-grade governance

| # | Criterion | How verified | Current status |
|---|-----------|--------------|----------------|
| B1 | Real maintainers/reviewers exist beyond the author/merger | CODEOWNERS + public GitHub identities | **Not met** — current trust-critical ownership is interim `@fraware`; role vacancies remain TBA |
| B2 | Trust-critical branch protection and required code-owner review are enabled | GitHub repository settings | **Not independently verified / not claimed** — see [governance_verification.md](governance_verification.md) |
| B3 | Promoted claims cannot be self-reviewed or self-promoted | governance rule + protected branch + validation | **Not met end-to-end** |
| B4 | Every promoted claim has two authenticated, independent review attestations | `review_attestation_v2` + public review event | **Not met** — legacy alias reviewers are not authenticated identity; issue #12; [promotion freeze](promotion_freeze.md) |
| B5 | Open audit findings are represented by actual public GitHub issues | GitHub issues | **Partially met** — local `QSB-AUD-*` stubs alone do not satisfy this criterion |
| B6 | Contribution and second-kernel policies are explicit | CONTRIBUTING/GOVERNANCE/adapter docs | Met as documentation, but does not satisfy B1–B5 |

**QSpecBench must not currently be called community-grade.** Named role labels with a sole interim owner are not independent maintainers, and local audit IDs are not public issue tracking. Empty gold inventory under the v1 demotion is intentional honesty, not governance completion.

---

## Level C — scientific reference suite

The repository contains selected real checked claims under declared scopes. The full scientific reference-suite target is stronger than any single machine-closed package. The five criteria below correspond one-to-one to the required capabilities in `docs/release_v1_contract.yaml`; a capability remains unsatisfied until a benchmark is explicitly assigned and strict qualification verifies reference maturity, corpus membership, assurance closure, and required independent reviews.

| # | Criterion | Required scientific result | Current status |
|---|-----------|----------------------------|----------------|
| C1 | Real compiler transformation | Compiler/version/config-bound source→target artifacts with exact semantic equivalence and independent supporting checker | **Machine-closed experimental instance** (`qiskit_optimize_1q_gates_hxx_identity`); not gold; not a general Qiskit theorem — [flagship](flagships/compiler_transformation_equivalence.md) |
| C2 | Full dynamic protocol | Arbitrary-input protocol with formal measurement/instrument, classical feed-forward, and final subsystem correctness | **Machine-closed experimental pure-state instrument** (`teleportation_dynamic_feedforward_protocol`); not mixed-state CPTP; not gold — [flagship](flagships/dynamic_teleportation.md) |
| C3 | QEC assurance chain | Keep code/family validity, distance, syndrome extraction, decoder contract, correction/logical preservation and repeated rounds distinct; include non-toy certificate path | **Partially met** — layered three-qubit bit-flip package is `experimental_closed`; external/family work remains open — [flagship](flagships/qec_bit_flip_chain.md) |
| C4 | Operator-level Hamiltonian approximation | Formally checked product-formula error in operator norm or stronger declared metric | **Narrowed machine-closed instance** (Frobenius majorant for X,Z at t=π/4); not a general operator-norm Lie-Trotter theorem — [flagship](flagships/hamiltonian_product_formula.md) |
| C5 | Semantically adjudicated AI formalization | Explicit source→formal relation; kernel-valid strict weakening cannot score as semantic equivalence | **Not met as gold** — packages demoted; historical alias reviews are not authenticated independent review — issue #16 |

Existing checked results retain their exact scopes. Machine closure is not independent review and is not rhetorical expansion into Level C completion.

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
10. Scientific flagships satisfy Level C under authentic review where gold is claimed.

The external reproduction program (issue #9) is explicitly excluded from v1 and is not silently counted as completed here.

---

## Permanent residuals and scope discipline

The following principles are permanent even after Levels A–D improve:

- The open-ended QEC obligation `unbounded_all_codes_mwpm` remains outside checked scope; finite code/distance/decoder evidence does not discharge it.
- Device `hardware_semantics`, `device_fidelity`, and `pulse_schedule_semantics` are not implied by a software ISA abstraction.
- Unnormalized `denotateOps3C` Toffoli equality remains outside the normalized Clifford+T proposition; the normalization choice must stay explicit.
- A finite Stim/PyMatching declared universe such as `stim_repetition_memory_odd_d_le_7_R_eq_d_p0p01` is not all-code fault tolerance.
- A distance certificate is not syndrome-extraction-circuit correctness.
- A QCEC result is externally trusted supporting evidence unless its trust model is strengthened; it does not by itself define the semantic proposition.
- A kernel-checked theorem establishes the formal theorem under its assumptions, not the faithfulness of the theorem to a natural-language source claim.
- Entry-wise numerical error, finite sampling, or `N * epsilon` bookkeeping is not an operator-level Hamiltonian approximation theorem.
- QBricks/ZX/Coq/Rocq/Isabelle adapters or stubs are not badges of completeness; trust depends on the actual executed evidence path.
- Lean-QEC interoperability is distance-only (`BB90_dist_10`); a passing cold native result for one exact SHA does not transfer to another release candidate, which must independently rerun and pass the lane.
- Corpus-executed code uses constrained execution paths but is not a general sandbox product.

Never resolve a missing guarantee by renaming it into checked scope. Narrow the proposition or leave the obligation open.

---

## Live corpus snapshot

Source of truth: [generated_status.md](generated_status.md) and [status.md](status.md). Regenerate rather than hand-editing counts.

v1 completion branch (regenerate to confirm):

- `experimental_closed`: 21 (machine closure; **not** independent review)
- `reference_claim`: 0
- `artifact_bound_reference_claim`: 0
- gold promoted inventory: 0
- total benchmarks excluding template: 52
- checked headlines under declared scope: 21
- benchmarks with some checked evidence: 48

These counts are descriptive corpus state. They do **not** establish Level B community governance or Level C scientific-reference-suite completion. The canonical release contract uses the 21 `experimental_closed` packages as part of the non-vacuous release-assurance corpus even while the reference inventory is zero.

Public implementation blockers and migration work are tracked in issues #12–#18.

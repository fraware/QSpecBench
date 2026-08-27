# release_audit_v1

Decision: **revise**

This tree is the v1 engineering substrate plus honest demotion of the former gold claims and four machine-closed experimental flagship packages. It is not yet an immutable tagged release and does not yet satisfy the full v1 contract in [release_v1_criteria.md](release_v1_criteria.md).

## Required audit list

| Item | Status |
|---|---|
| Empty/demoted gold inventory | Met in this tree (RC/ABRC count is 0) |
| Flagship machine-closure | Compiler (Qiskit Optimize1qGates H;X;X instance), dynamic teleportation (arbitrary pure-state instrument, not mixed-state CPTP), Hamiltonian (Frobenius-majorant X,Z instance at t=pi/4; not a general operator-norm Lie-Trotter theorem), three-qubit bit-flip layered QEC are packaged as `experimental_closed` under declared domains |
| Lean-QEC structured result | **Demonstrated for the pinned BB90 state.** Exact-head PR workflow at `cce598d94acdd368d77001e790eb0847353d914e` produced `ok=true`, `kernel_checked=true`, `acceptance.status=passing`, `kernel_typechecking_bypassed=false`, `upstream_default_reproduced=true`, and `fallback_used=false` against upstream commit `c9c85603ab522b9f7df6315ed51513bcfb95fd90`. This evidence does not transfer to a future release-candidate SHA; that candidate must rerun and pass the lane. |
| Branch-protection evidence | **Not met** — live repository inspection on 27 Aug 2026 reports `main` as unprotected (`protected: false`); issue #19 remains open |
| #9 exclusion | Explicit; not claimed |
| Residual: no independent reviewers | Explicit; community-grade governance remains unmet |

## Ship gate

Only `ship` tags `v1.0.0`. This audit remains `revise`. Engineering substrate checks and Lean-QEC interoperability can pass while other release-contract gates remain unmet. The stronger contract in [release_v1_criteria.md](release_v1_criteria.md) remains authoritative; this audit must not redefine v1 downward merely to make the tree shippable.

## Revise taxonomy

### (A) Governance / scope residuals

These are explicit current facts. They remain blockers wherever the v1 contract requires the corresponding governance property; they must not be silently reclassified as engineering success.

1. **No independent reviewers** — gold/RC/ABRC inventory stays empty; alias YAML is `unauthenticated_legacy_review` only. Community-grade governance is not met.
2. **Branch protection is disabled** — live GitHub state on 27 Aug 2026 reports `main` with `protected: false`. Required protection, code-owner review, conversation resolution, and anti-self-promotion enforcement remain issue #19 work.
3. **Issue #9 out of scope** — independent third-party cold-host reproduction remains `post-v1` and is not counted as completed.
4. **Lean-QEC evidence is exact-head evidence** — cold native acceptance is demonstrated for `cce598d94acdd368d77001e790eb0847353d914e`, but a later release candidate must independently rerun and pass the same fail-closed lane. Do not transfer a prior SHA's result to a new candidate.

### (B) Remaining engineering / release-contract blockers

1. **Canonical release-gate convergence** — the documented strict candidate checks, CI validation, and tag/release workflow must converge on one fail-closed release contract rather than separate partially overlapping gates. The final release path must enforce strict corpus/assurance-graph validation and the candidate verification contract rather than relying on ordinary validation or a smoke bundle alone.
2. **SBOM requirement** — the current release tooling provides dependency/SBOM-lite metadata, but the v1 contract requires a real release SBOM. A stub or summary is not sufficient.
3. **Release-corpus assurance migration (#13)** — the non-vacuous release contract is implemented, but every package selected into the canonical release corpus must still have the required closed assurance graph before strict qualification can pass. Semantic-profile authority (#14) is implemented and merged in #32; typed-adapter execution identity (#15) is implemented and merged in #30. Those closed milestones must not be described as remaining migrations.
4. **Immutable release evidence** — no `v1.0.0` exact-head candidate has yet completed the final bundle/provenance/archive path required by the v1 contract. A green development or repository-closeout commit is not an immutable release.

### (C) Scientific / governance contract blockers

The repository's v1 criteria make scientific depth and governance separate release gates, not optional prose. Current evidence therefore keeps this audit at `revise` even after the engineering substrate becomes cleaner:

- Level B community governance remains incomplete: independent maintainers/reviewers, branch protection, anti-self-promotion enforcement, and authenticated independent review are not established end-to-end.
- Level C remains scoped rather than complete: compiler, dynamic-protocol, QEC, and Hamiltonian flagships have meaningful machine-closed instances under declared domains, but the stronger reference-suite targets remain narrower/partial as documented in [definition_of_completion.md](definition_of_completion.md); AI formalization is not gold or independently adjudicated.
- The five Level-C capability assignments in `release_v1_contract.yaml` remain subject to genuine reference maturity, assurance closure, and independent review. Empty assignments are a blocker, not evidence of completion.

## Closed implementation milestones

- PR #30 closed the typed-adapter execution-identity migration (#15).
- PR #31 established the non-vacuous machine-readable v1 release contract, while intentionally leaving strict scientific qualification unsatisfied.
- PR #32 closed semantic-profile authority (#14) with versioned executable static/dynamic v2 profiles, strict grammar, explicit numeric semantics, bridge/profile cross-checks, and regression coverage. Historical semantic profiles remain immutable rather than silently reinterpreted.
- Promotion Check now runs on pushes to `main` as well as pull requests, allowing an exact merge/closeout SHA to receive its own promotion-gate result instead of inheriting a PR-head result.

These milestones reduce engineering ambiguity. They do not satisfy #12, #13, #16–#23 or convert the audit from `revise` to `ship`.

## Lean-QEC acceptance history

Local cold attempts on 25 Aug 2026 failed before theorem acceptance because of host disk exhaustion: first during required LFS materialization, then during elan/toolchain/lake-cache installation after LFS verification succeeded. Those failures were infrastructure failures, not mathematical disproofs and not green evidence.

On 26 Aug 2026, after correcting the provenance pin to the immediately pre-corruption upstream commit `c9c85603ab522b9f7df6315ed51513bcfb95fd90` while preserving the theorem source blob, Lean toolchain, and dependency graph, the exact-head PR workflow at `cce598d94acdd368d77001e790eb0847353d914e` completed the cold root-project `olean` build and emitted native kernel acceptance with no fallback. This establishes the pinned BB90 distance evidence path for that exact QSpecBench head; it does not establish broader QEC obligations such as syndrome-extraction semantics, physical noise, decoder correctness, logical-preservation correction, or repeated-round fault tolerance.

## Public language

Do not say independently reviewed, community-grade, full-reference-suite complete, release-reproduced, or `v1.0.0`-ready except where the corresponding gate is actually met. For Lean-QEC, it is accurate to say that the pinned `BB90_dist_10` distance theorem has demonstrated cold native kernel acceptance on the exact PR head cited above; do not generalize that result to other QEC obligations or later release SHAs.

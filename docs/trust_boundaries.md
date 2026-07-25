# Trust boundaries

Every benchmark declares a `trust_boundary` block.

## Fields

- **checked_by** — verified in this benchmark's evidence pipeline
- **trusted_kernels** — proof kernels relied upon (Lean 4 kernel in CI today; schema reserves Coq/Rocq/Isabelle types)
- **trusted_external_tools** — specialized tools (QCEC, QEC verifiers)
- **untrusted_components** — drafts, AI output, informal notes
- **assumptions_not_checked** — explicit assumptions not validated

## Trusted kernels

**Lean 4** is the sole proof-assistant kernel integrated in CI. SAT/SMT certificate checkers may anchor small-instance certificates.

## External tools

Tool output may be valuable but trust depends on the tool and independent checkability.

## Unchecked assumptions

Examples: ideal measurement semantics, QASM-to-semantics gap, decoder correctness assumed for QEC.

Some obligations are **permanent residuals** (device/pulse fidelity, unbounded
all-codes MWPM, unnormalized Toffoli denotation, QBricks/ZX as non-complete FV
coverage, Rocq/Isabelle stubs). They are documented — not promoted — in
[definition_of_completion.md](definition_of_completion.md) and the README.

## Untrusted components

AI drafts, informal derivations, unaudited scripts.

## Corpus-executed evidence (by design)

Python `simulation` scripts and SAT certificate adapters may execute code or
solver tooling declared by the corpus. That is intentional under a
**trust-the-corpus** model: maintainers review artifacts before promotion.

CI and `evidence_runner` apply a **constrained runner** for `simulation` /
`sat_certificate` evidence (`tools/qspecbench/evidence_sandbox.py`):

- wall-clock timeout (fail-closed)
- cwd jailed under the claim directory via `resolve_claim_path`
- proxy / network-related environment variables stripped
- OS resource limits (`RLIMIT_CPU` / `RLIMIT_AS`) where the platform allows

This reduces foot-guns for trusted corpus authors. It is **not** a multi-tenant
sandbox product and does not make arbitrary third-party uploads safe. Raw shell
`command:` evidence is fail-closed outside a maintainer escape hatch
(`QSPECBENCH_TRUSTED_LOCAL` + clean tree; disallowed in CI). See audit finding
**F-021** (closed as by-design; constrained runner is mitigation, not a product
sandbox).

The `human_review` adapter only checks length/keywords (heuristic). It **cannot**
satisfy `required_for_claim` for ABRC / `reference_claim` promotions — dual
hash-bound review JSON (schema `review_artifact.schema.json`, enforced by
`tools/qspecbench/reviews.py` and `status.reviews`) is the gate (**F-026**,
closed by design).

```bash
qspecbench trust benchmarks/<track>/<claim_id>/
```

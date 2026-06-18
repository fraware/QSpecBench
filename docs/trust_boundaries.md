# Trust boundaries

Every benchmark declares a `trust_boundary` block.

## Fields

- **checked_by** — verified in this benchmark's evidence pipeline
- **trusted_kernels** — proof kernels relied upon (**Lean 4 only** in this repository)
- **trusted_external_tools** — specialized tools (QCEC, QEC verifiers)
- **untrusted_components** — drafts, AI output, informal notes
- **assumptions_not_checked** — explicit assumptions not validated

## Trusted kernels

**Lean 4** is the sole proof-assistant kernel integrated in CI. SAT/SMT certificate checkers may anchor small-instance certificates.

## External tools

Tool output may be valuable but trust depends on the tool and independent checkability.

## Unchecked assumptions

Examples: ideal measurement semantics, QASM-to-semantics gap, decoder correctness assumed for QEC.

## Untrusted components

AI drafts, informal derivations, unaudited scripts.

```bash
qspecbench trust benchmarks/<track>/<claim_id>/
```

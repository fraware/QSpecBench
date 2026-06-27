# Versioning

QSpecBench versions three things separately so that progress in one does not imply maturity in the
others. Conflating them is how an evidence format starts to overclaim.

| Component | Field / source | Current | Meaning |
|---|---|---|---|
| Schema | `qspecbench_version` in each `spec.yaml`; `schema/qspecbench.schema.json` | `0.2` | The structure of a benchmark specification (fields, enums, validation contract). |
| Tooling | `qspecbench` CLI (`pyproject.toml`), `tools/qspecbench/__init__.py`, Lean lib (`lean/lakefile.lean`) | `0.2.0` | The validators, dashboard generator, bridge checker, and Lean proof library. |
| Corpus | the benchmark suite under `benchmarks/` | `0.1.0` | The collection of benchmarks and the evidence actually attached to them. |
| Release tag | git tag | `v0.1.0` | A tagged snapshot of schema + tooling + corpus together. |

## Why separate versions

- A new **schema** field (for example `claim_scope`) does not mean the **corpus** got more proofs.
- Better **tooling** (a stricter validator, a real kernel bridge) does not retroactively prove any
  benchmark headline claim.
- The **corpus** version is intentionally low (`0.1.0`): most entries are reference scaffolds, not
  proved headline claims. Raising it requires real `reference_claim` benchmarks, not more scaffolds.

## Raising the corpus version

The corpus version (`CORPUS_VERSION`, currently `0.1.0`) increases only when the **checked claim
content** of the suite materially improves — not when scaffolds or labels are added.

Suggested thresholds before bumping to `0.2.0`:

| Criterion | Target |
|-----------|--------|
| `reference_claim` benchmarks | ≥ 8 across ≥ 3 tracks |
| Kernel-checked semantic bridges | ≥ 5 equivalence entries with manifest + hashes |
| QEC correction claims checked | ≥ 1 small code with logical-preservation validator passing |
| Provenance wired | All file-backed artifacts listed in `spec.yaml` `provenance` |

Until those thresholds are met, keep `CORPUS_VERSION` at `0.1.0` even as tooling (`0.2.0`) and schema
(`0.2`) evolve.

## Hamiltonian artifact schema migration

Legacy Hamiltonian JSON artifacts without a top-level `type` field are tolerated only until corpus
**v0.2.0**. After that deadline (documented in `GOVERNANCE.md`), all Hamiltonian artifacts must
validate against `schema/hamiltonian.schema.json`. Migration started in v0.1.x: `heisenberg_model`
and `bravyi_kitaev` artifacts now declare `type: pauli_hamiltonian`.

## Single source of truth

The canonical version constants live in `tools/qspecbench/__init__.py`
(`SCHEMA_VERSION`, `TOOLING_VERSION`, `CORPUS_VERSION`, `RELEASE_TAG`) and are echoed by the
dashboard generator (`qspecbench dashboard`). Keep `pyproject.toml`, `lean/lakefile.lean`,
`CITATION.cff`, and the README versions table consistent with those constants.

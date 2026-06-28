# Versioning

QSpecBench versions three things separately so that progress in one does not imply maturity in the
others. Conflating them is how an evidence format starts to overclaim.

| Component | Field / source | Current | Meaning |
|---|---|---|---|
| Schema | `qspecbench_version` in each `spec.yaml`; `schema/qspecbench.schema.json` | `0.2` | The structure of a benchmark specification (fields, enums, validation contract). |
| Tooling | `qspecbench` CLI (`pyproject.toml`), `tools/qspecbench/__init__.py`, Lean lib (`lean/lakefile.lean`) | `0.2.0` | The validators, dashboard generator, bridge checker, and Lean proof library. |
| Corpus | the benchmark suite under `benchmarks/` | `0.2.0` | The collection of benchmarks and the evidence actually attached to them. |
| Release tag | git tag | `v0.2.0` | A tagged snapshot of schema + tooling + corpus together. |

## Why separate versions

- A new **schema** field (for example `claim_scope`) does not mean the **corpus** got more proofs.
- Better **tooling** (a stricter validator, a real kernel bridge) does not retroactively prove any
  benchmark headline claim.
- The **corpus** version tracks checked claim content, not scaffold count alone.

## Corpus v0.2.0 gate checklist (satisfied 2026-06-27)

| Criterion | Target | Status | Footnote |
|-----------|--------|--------|----------|
| `reference_claim` benchmarks | ≥ 8 across ≥ 3 tracks | **Met** (8 total: 6 equivalence/algorithms, 1 Hamiltonian, 1 QFT pair) | QEC bit-flip remains `reference_scaffold` with narrowed headline (decoder assumed) |
| Manifest-checked theorem bindings | ≥ 5 equivalence/algorithm entries | **Met** (11 manifest bridges) | Distinct from `kernel_checked_artifact_semantics` (5 in working tree) |
| QEC correction claims checked | ≥ 1 small code with logical-preservation validator | **Met** | `three_qubit_bit_flip_code_corrects_one_x`: tables + brute-force preservation; decoder algorithm assumed |
| Provenance wired | All file-backed artifacts in `spec.yaml` `provenance` | **Met** | Drift fails validation |

**Not claimed at v0.2.0 tag:** QEC `reference_claim` with proved decoder; full OpenQASM3 / dynamic semantics.
**Working tree (post-v0.2.1):** five `kernel_checked_artifact_semantics` bridges (codegen + kernel proofs).

## Raising the corpus version further

Suggested thresholds before bumping to `0.3.0`:

| Criterion | Target |
|-----------|--------|
| `kernel_checked_artifact_semantics` bridges | ≥ 1 with codegen + kernel proof | **Met in working tree** (5 bridges) |
| QEC `reference_claim` | ≥ 1 with decoder correctness checked, not assumed |
| Teleportation or major protocol | ≥ 1 `reference_claim` with relational semantics |

## Hamiltonian artifact schema migration

Legacy Hamiltonian JSON artifacts without a top-level `type` field were tolerated until corpus
**v0.2.0**. Migration completed in v0.1.x: all Hamiltonian artifacts now declare a typed schema
(`pauli_hamiltonian`, `fermionic_hamiltonian`, `trotter_step`, etc.). Validators reject untyped files.

## Single source of truth

The canonical version constants live in `tools/qspecbench/__init__.py`
(`SCHEMA_VERSION`, `TOOLING_VERSION`, `CORPUS_VERSION`, `RELEASE_TAG`) and are echoed by the
dashboard generator (`qspecbench dashboard`). Keep `pyproject.toml`, `lean/lakefile.lean`,
`CITATION.cff`, and the README versions table consistent with those constants.

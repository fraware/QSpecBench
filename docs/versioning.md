# Versioning

QSpecBench versions three things separately so that progress in one does not imply maturity in the
others. Conflating them is how an evidence format starts to overclaim.

| Component | Field / source | Current | Meaning |
|---|---|---|---|
| Schema | `qspecbench_version` in each `spec.yaml`; `schema/qspecbench.schema.json` | `0.2` | The structure of a benchmark specification (fields, enums, validation contract). |
| Tooling | `qspecbench` CLI (`pyproject.toml`), `tools/qspecbench/__init__.py`, Lean lib (`lean/lakefile.lean`) | `0.2.0` | The validators, dashboard generator, bridge checker, and Lean proof library. |
| Corpus | the benchmark suite under `benchmarks/` | `0.2.0` | The collection of benchmarks and the evidence actually attached to them. |
| Release tag | git tag | `v0.2.1` | A tagged snapshot of schema + tooling + corpus together. |

## Why separate versions

- A new **schema** field (for example `claim_scope`) does not mean the **corpus** got more proofs.
- Better **tooling** (a stricter validator, a real kernel bridge) does not retroactively prove any
  benchmark headline claim.
- The **corpus** version tracks checked claim content, not scaffold count alone.

## v0.2 release honesty

The **v0.2.0** tag is a schema and tooling milestone, not a claim that the corpus is fully
proved. Most benchmarks remain **reference scaffolds** with honest trust boundaries. Only
benchmarks at **`reference_claim`** maturity (or the future **`artifact_bound_reference_claim`**
tier documented below) assert a checked headline under declared scope.

What v0.2 **does** provide:

- A stable evidence format (`qspecbench_version: "0.2"`) with fail-closed validation
- Six **kernel-checked codegen-trace** bridges (AST hash chain + Lean kernel proof)
- One QEC small-code correction check with table-backed preservation (decoder algorithm assumed)
- CI that runs schema validation, evidence adapters, Lean compile, and bridge verification

What v0.2 **does not** claim:

- Full OpenQASM 3 or dynamic-circuit semantics for all protocol benchmarks
- QEC `reference_claim` with a proved decoder (bit-flip remains `reference_scaffold` with narrowed headline)
- That manifest-checked theorem bindings prove artifact semantics end-to-end

See [versioning.md](versioning.md) for the corpus gate checklist and [status.md](status.md) for per-benchmark breakdown.

## Maturity tiers

| `status.maturity` | Meaning |
|---|---|
| `seed` / `usable` | Early or contributor-ready package |
| `reference_scaffold` | Reference format example; headline not checked |
| `reference_contract` | Machine spec complete; evidence partial |
| `reference_artifact` | Artifacts validated; claim still open |
| `reference_claim` | Headline checked under declared scope (`headline_claim_status.checked_under`) |
| `artifact_bound_reference_claim` | **Reserved tier (schema only):** headline checked and explicitly bound to named artifact hashes + checker chain. Not assigned to any benchmark in v0.2. |

## Corpus v0.2.0 gate checklist (satisfied 2026-06-27)

| Criterion | Target | Status | Footnote |
|-----------|--------|--------|----------|
| `reference_claim` benchmarks | ≥ 8 across ≥ 3 tracks | **Met** (8 total: 6 equivalence/algorithms, 1 Hamiltonian, 1 QFT pair) | QEC bit-flip remains `reference_scaffold` with narrowed headline (decoder assumed) |
| Manifest-checked theorem bindings | ? 5 equivalence/algorithm entries | **Met** (11 manifest bridges) | Distinct from kernel-checked codegen-trace bridges (5; see `kernel_checked_codegen_trace`) |
| QEC correction claims checked | ≥ 1 small code with logical-preservation validator | **Met** | `three_qubit_bit_flip_code_corrects_one_x`: tables + brute-force preservation; decoder algorithm assumed |
| Provenance wired | All file-backed artifacts in `spec.yaml` `provenance` | **Met** | Drift fails validation |

**Not claimed at v0.2.0 tag:** QEC `reference_claim` with proved decoder; full OpenQASM3 / dynamic semantics.
**Working tree (post-v0.2.1):** six kernel-checked codegen-trace bridges (`kernel_checked_codegen_trace`; codegen AST hash chain + kernel proofs); Lean `BridgeMetadata` pins for all six; CI run [28395530818](https://github.com/QSpecBench/QSpecBench/actions/runs/28395530818) on tag `v0.2.1` (commit `278119a`).

## v0.2.1 release notes (2026-06-29)

Tag **`v0.2.1`** (`278119a`) is an incremental tooling and honesty milestone on top of v0.2.0 — not a
corpus-wide proof advance.

**Scope (honest):**

- Six **kernel-checked codegen-trace** bridges with read-only verify, `theorem_source_statement_hash`, and Lean `BridgeMetadata` manifest pins (hashes from manifest, not elaborator export)
- Incremental Lean dynamic semantics: `Measurement.lean` classical-bit recording stub, conditional Pauli on `Fin 4`/`Fin 8`, basis-state teleportation lemma chain (no `sorry`)
- `parseQasmSource` expansion for Bell and SWAP exact on-disk kernel artifact grammars
- QEC dashboard split: `qec_small_code_checked` vs `qec_external_certificate_checked`; witness hash backfill
- Governance: `artifact_bound_reference_claim` promotion checklist (schema only; no benchmark promoted), Coq excluded from maturity until CI-bound proof, ai_formalization reviewer warnings
- Corrupt-verify tests for swap and bell Generated modules

**Not claimed at v0.2.1:**

- `artifact_bound_reference_claim` assigned to any benchmark
- Full OpenQASM 3 / dynamic-circuit kernel semantics for teleportation relational claim
- Coq proofs in default CI
- QEC `reference_claim` with proved decoder

## Raising the corpus version further

Suggested thresholds before bumping to `0.3.0`:

| Criterion | Target |
|-----------|--------|
| Kernel-checked codegen-trace bridges | ? 1 with codegen AST hash chain + kernel proof | **Met in working tree** (5 bridges) |
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

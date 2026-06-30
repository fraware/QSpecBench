# Versioning

QSpecBench versions three things separately so that progress in one does not imply maturity in the
others. Conflating them is how an evidence format starts to overclaim.

| Component | Field / source | Current | Meaning |
|---|---|---|---|
| Schema | `qspecbench_version` in each `spec.yaml`; `schema/qspecbench.schema.json` | `0.3` | The structure of a benchmark specification (fields, enums, validation contract). |
| Tooling | `qspecbench` CLI (`pyproject.toml`), `tools/qspecbench/__init__.py`, Lean lib (`lean/lakefile.lean`) | `0.2.0` | The validators, dashboard generator, bridge checker, and Lean proof library. |
| Corpus | the benchmark suite under `benchmarks/` | `0.2.0` | The collection of benchmarks and the evidence actually attached to them. |
| Release tag | git tag | `v0.2.3` | A tagged snapshot of schema + tooling + corpus together. |

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
| `artifact_bound_reference_claim` | **Reserved tier (schema v0.2+):** headline checked and explicitly bound to named artifact hashes + checker chain. Assigned to kernel-bridge pilots (see v0.2.3 notes). |

## Corpus v0.2.0 gate checklist (satisfied 2026-06-27)

| Criterion | Target | Status | Footnote |
|-----------|--------|--------|----------|
| `reference_claim` benchmarks | ≥ 8 across ≥ 3 tracks | **Met** (8 total: 6 equivalence/algorithms, 1 Hamiltonian, 1 QFT pair) | QEC bit-flip remains `reference_scaffold` with narrowed headline (decoder assumed) |
| Manifest-checked theorem bindings | ≥ 5 equivalence/algorithm entries | **Met** (11 manifest bridges) | Distinct from kernel-checked codegen-trace bridges (6; see `kernel_checked_codegen_trace`) |
| QEC correction claims checked | ≥ 1 small code with logical-preservation validator | **Met** | `three_qubit_bit_flip_code_corrects_one_x`: tables + brute-force preservation; decoder algorithm assumed |
| Provenance wired | All file-backed artifacts in `spec.yaml` `provenance` | **Met** | Drift fails validation |

**Not claimed at v0.2.0 tag:** QEC `reference_claim` with proved decoder; full OpenQASM3 / dynamic semantics.
**Working tree (post-v0.2.3):** six `kernel_checked_artifact_semantics` bridges with `ast_authority: lean_mirror`; elaborator hash primary authority (schema **0.3**); tag `v0.2.3` (commit `49e8899`).

## v0.2.3 release notes (2026-06-29)

Tag **`v0.2.3`** (`49e8899`) is a middle-tier closure milestone: governance sync, AST authority transition, and elaborator hash as v0.3 primary gate.

**Scope (honest):**

- **`artifact_bound_reference_claim` pilots:** six kernel bridges (CNOT, Bell prep, H-X-H, H-H cancel, SWAP-from-CX, Toffoli CCX source) with dual named reviews and hash anchor chain
- Six **`kernel_checked_artifact_semantics`** bridges with `lean_ast_sha256` + `ast_authority: lean_mirror` (Python `ast_sha256` secondary cross-check)
- **`theorem_elaborator_hash`** from `ExportTheoremTypesCheck.lean` + `scripts/export_theorem_types.py` (primary); regex `theorem_source_statement_hash` warning-only when elaborator cache present
- Schema bump to **0.3** for elaborator/AST authority fields; tooling/corpus remain **0.2.0**
- Pinned **`uv.lock`** in release SBOM

**Not claimed at v0.2.3:**

- Full Toffoli decomposition kernel equivalence (target-side trace open)
- QEC `reference_claim` with proved decoder
- Teleportation or major protocol `reference_claim`
- Git tag on remote (process step; `RELEASE_TAG` constant updated)

## v0.2.2 release notes (2026-06-29)

Tag **`v0.2.2`** (`e5ee749`) is a documentation and middle-tier engineering milestone on top of v0.2.1.

**Scope (honest):**

- Six **kernel-checked codegen-trace** bridges with `parseQasmSource` artifact binding pilot (CNOT byte chain)
- `qspecbench bridge-metadata verify` CLI + CI gate
- `theorem_source_statement_hash` remains **syntactic only** (not elaborator export); v0.3 adds `theorem_elaborator_hash`
- CNOT `artifact_bound_reference_claim` pilot promotion path documented in GOVERNANCE.md

**Not claimed at v0.2.2:**

- Full `kernel_checked_artifact_semantics` label on all six bridges (Phase 2)
- Elaborator/type hash as primary theorem authority (Phase 3 / v0.3.0)
- QEC `reference_claim` with proved decoder

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
| Kernel-checked codegen-trace bridges | ≥ 1 with codegen AST hash chain + kernel proof | **Met in working tree** (6 bridges) |
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

# Contributing to QSpecBench

Thank you for contributing. Every benchmark must include:

1. A human-readable claim card (`README.md`)
2. A machine-readable specification (`spec.yaml`)
3. Explicit assumptions and trust boundary
4. Artifacts and evidence in the correct subdirectories

## Developer setup

1. Install dependencies with `uv sync --frozen --extra dev`.
2. **Install pre-commit hooks** (required for PRs that touch Python, schema, Lean generated ops, or the audit ledger):

   ```bash
   uv run pre-commit install
   uv run pre-commit run --all-files
   ```

   The config is [`.pre-commit-config.yaml`](.pre-commit-config.yaml) (ruff + ruff-format, schema examples, generated-ops integrity, audit YAML parse). CI also runs `ruff check` as a hard gate; local pre-commit catches the same class of issues earlier.
3. Schema **0.3** is the active dialect. Gold/`reference_claim`/`artifact_bound_reference_claim`
   promotions are **frozen for v1** without authentic independent reviewers — see
   [docs/promotion_freeze.md](docs/promotion_freeze.md). Machine-closed packages use
   `experimental_closed`. Schema migration notes: [docs/schema_migration_0.3.md](docs/schema_migration_0.3.md)
   (and [0.2](docs/schema_migration_0.2.md) for earlier fields).
4. Track maintainer roles and CODEOWNERS policy: [GOVERNANCE.md](GOVERNANCE.md).
5. **Lean proofs are optional locally** ([Lean setup](docs/lean_setup.md)); CI installs elan and
   runs `lake build`. If you add or change Lean evidence:

   ```bash
   cd lean && lake build
   ```

   **Never** import `QSpecBench.Evidence.All` into the root `lean/QSpecBench.lean` — it is a
   separate, heavier target built on its own to avoid CI out-of-memory failures:

   ```bash
   cd lean && lake build QSpecBench.Evidence.All
   ```

## Adding a benchmark

Follow [docs/adding_a_benchmark.md](docs/adding_a_benchmark.md). Copy an existing seed benchmark in the appropriate track and adapt it.

## Good first benchmark

Start from the shared scaffold, then copy a track seed that matches your claim type:

1. **Scaffold** — [`benchmarks/_template/`](benchmarks/_template/) (`spec.yaml`, `README.md`, `artifacts/`, `notes/`)
2. **Track seeds** — pick one reference exemplar in the target track:
   - Algorithms: [`teleportation_preserves_state_up_to_pauli_correction`](benchmarks/algorithms/teleportation_preserves_state_up_to_pauli_correction/)
   - Equivalence: [`cnot_self_inverse_cancellation`](benchmarks/equivalence/cnot_self_inverse_cancellation/)
   - QEC: [`three_qubit_bit_flip_code_corrects_one_x`](benchmarks/qec/three_qubit_bit_flip_code_corrects_one_x/)
   - Hamiltonian: [`small_fermionic_hamiltonian_is_hermitian`](benchmarks/hamiltonian/small_fermionic_hamiltonian_is_hermitian/)
   - AI formalization: [`formalize_no_cloning_statement`](benchmarks/ai_formalization/formalize_no_cloning_statement/)
3. **Schema examples** — non-runnable templates in [`schema/examples/`](schema/examples/) (v0.2 field shapes)
4. **Validate** — `qspecbench validate benchmarks/<your_id>/` before opening a PR

Usable maturity is fine for a first contribution; reference promotion follows [docs/reference_benchmarks.md](docs/reference_benchmarks.md).

## Pull request checklist

- [ ] Directory placed under correct track
- [ ] `spec.yaml` validates (`qspecbench validate`)
- [ ] `id` matches directory name (lowercase snake_case)
- [ ] Artifact and evidence paths resolve
- [ ] Trust boundary is explicit
- [ ] Maturity level is honest
- [ ] No unsupported proof claims in README
- [ ] Pre-commit hooks pass locally (`uv run pre-commit run --all-files`)
- [ ] Dashboard regenerated if corpus counts change: `qspecbench dashboard benchmarks/ --out docs/status.md`
- [ ] CI passes

Local CI/release dry-run commands (no commit/push required): [docs/release_prep_notes.md](docs/release_prep_notes.md).

## Reference benchmarks

Reference maturity requires checked evidence, declared checker, passing CI, and explicit assumptions.

**Promotion workflow:**

1. Open a [Reference promotion proposal](.github/ISSUE_TEMPLATE/reference_promotion.yml) issue.
2. Ensure evidence stack meets the checklists in [docs/reference_benchmarks.md](docs/reference_benchmarks.md) and track norms.
3. Add or update `semantic_bridge` when both QASM and Lean evidence are present.
4. Document `proof_obligations` for multi-lemma reference claims (schema 0.2+).
5. Obtain scientific, specification, and evidence review per [GOVERNANCE.md](GOVERNANCE.md).

### ABRC checklist

Before setting `status.maturity: artifact_bound_reference_claim`, complete the full
[`artifact_bound_reference_claim` promotion checklist](docs/reference_benchmarks.md#artifact_bound_reference_claim-promotion-checklist)
(also mirrored in [GOVERNANCE.md](GOVERNANCE.md) under ABRC). Schema field shapes:
[docs/schema_migration_0.3.md](docs/schema_migration_0.3.md).

See [docs/schema_migration_0.2.md](docs/schema_migration_0.2.md) for fields introduced in v0.2.

## Proof assistants

**Lean 4 is the only proof assistant in default CI** (Lean-primary policy; see
[GOVERNANCE.md](GOVERNANCE.md) § Second-kernel policy). Add proofs under
`lean/QSpecBench/` and wire `lean_proof` evidence. CI runs `lake build`.
Coq / Rocq / Isabelle are discovery/opt-in only (`coq_proof` stubs, `QSPECBENCH_COQ=1`);
they do not affect maturity tiers.

## AI-generated content

Label AI output as `ai_draft` with `untrusted` trust level unless independently checked and semantically reviewed.

## Code of conduct

Be respectful and precise about verification claims. Do not call a benchmark "verified" without a declared checker.

# Contributing to QSpecBench

Thank you for contributing. Every benchmark must include:

1. A human-readable claim card (`README.md`)
2. A machine-readable specification (`spec.yaml`)
3. Explicit assumptions and trust boundary
4. Artifacts and evidence in the correct subdirectories

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
- [ ] CI passes

## Reference benchmarks

Reference maturity requires checked evidence, declared checker, passing CI, and explicit assumptions.

**Promotion workflow:**

1. Open a [Reference promotion proposal](.github/ISSUE_TEMPLATE/reference_promotion.yml) issue.
2. Ensure evidence stack meets [reference_benchmarks.md](docs/reference_benchmarks.md) checklist (when published) and track norms.
3. Add or update `semantic_bridge` when both QASM and Lean evidence are present.
4. Document `proof_obligations` for multi-lemma reference claims (schema 0.2).
5. Obtain scientific, specification, and evidence review per [GOVERNANCE.md](GOVERNANCE.md).

See [docs/schema_migration_0.2.md](docs/schema_migration_0.2.md) for schema fields introduced in v0.2.

## Proof assistants

**Lean 4 only.** Add proofs under `lean/QSpecBench/` and wire `lean_proof` evidence. CI runs `lake build`.

## AI-generated content

Label AI output as `ai_draft` with `untrusted` trust level unless independently checked and semantically reviewed.

## Code of conduct

Be respectful and precise about verification claims. Do not call a benchmark "verified" without a declared checker.

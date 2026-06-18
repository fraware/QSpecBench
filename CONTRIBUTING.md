# Contributing to QSpecBench

Thank you for contributing. Every benchmark must include:

1. A human-readable claim card (`README.md`)
2. A machine-readable specification (`spec.yaml`)
3. Explicit assumptions and trust boundary
4. Artifacts and evidence in the correct subdirectories

## Adding a benchmark

Follow [docs/adding_a_benchmark.md](docs/adding_a_benchmark.md). Copy an existing seed benchmark in the appropriate track and adapt it.

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

## Proof assistants

**Lean 4 only.** Add proofs under `lean/QSpecBench/` and wire `lean_proof` evidence. CI runs `lake build`.

## AI-generated content

Label AI output as `ai_draft` with `untrusted` trust level unless independently checked and semantically reviewed.

## Code of conduct

Be respectful and precise about verification claims. Do not call a benchmark "verified" without a declared checker.

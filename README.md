# QSpecBench

QSpecBench is a benchmark and evidence format for quantum formal verification.

It turns quantum-computing correctness claims into structured benchmark entries containing:

- an informal claim;
- a machine-readable specification;
- executable artifacts;
- declared assumptions;
- acceptable evidence paths;
- current evidence status;
- explicit trust boundaries.

[![CI](https://github.com/qspecbench/qspecbench/actions/workflows/validate.yml/badge.svg)](https://github.com/qspecbench/qspecbench/actions/workflows/validate.yml)

## Why this exists

Quantum formal verification lacks a common layer for comparing claims, tools, and evidence. QSpecBench provides that layer without conflating claims, artifacts, evidence, and proofs.

## What counts as a benchmark

A benchmark is not just a circuit. A benchmark is a **claim** plus a **specification** plus **artifacts** plus **evidence** plus a **trust boundary**.

## Tracks

- [Algorithms](benchmarks/algorithms/) — protocol and algorithm correctness
- [Equivalence](benchmarks/equivalence/) — circuit and compiler equivalence
- [QEC](benchmarks/qec/) — error correction claims
- [Hamiltonian](benchmarks/hamiltonian/) — simulation and resource claims
- [AI formalization](benchmarks/ai_formalization/) — AI-assisted formalization evaluation

## Trust model

QSpecBench distinguishes checked **Lean 4** proofs, tool-checked evidence, heuristic evidence, human review, and AI-generated drafts. This repository uses **Lean only** for proof-assistant evidence in CI. Simulation is evidence, not proof. LLM output is untrusted unless independently checked.

## Getting started

```bash
# Lean 4 proofs (CI installs elan automatically)
cd lean && lake build

pip install -e ".[dev]"
qspecbench validate benchmarks/
qspecbench check-evidence benchmarks/equivalence/cnot_self_inverse_cancellation/
qspecbench status benchmarks/
qspecbench dashboard benchmarks/ --out docs/status.md
pytest
```

## Current status

See the [dashboard](docs/status.md).

## Release readiness

| Criterion | Status |
|-----------|--------|
| Versioned schema + validator | Done |
| 34 benchmarks across 5 tracks | Done |
| Claim cards + `spec.yaml` per benchmark | Done |
| Lean 4 proofs in CI | Done (`lake build`) |
| Reference benchmark with kernel-checked proof | Done (`cnot_self_inverse_cancellation`) |
| Explicit trust boundaries | Done |
| Tool-neutral evidence adapters | Done (Lean-only PA) |
| Public dashboard | Done |
| Contributor docs + templates | Done |

Remaining frontier work: more kernel-checked Lean proofs, QCEC in CI, additional reference benchmarks.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/adding_a_benchmark.md](docs/adding_a_benchmark.md).

## Documentation

- [Claim model](docs/claim_model.md)
- [Schema reference](docs/schema_reference.md)
- [Evidence model](docs/evidence_model.md)
- [Trust boundaries](docs/trust_boundaries.md)
- [Lean setup](docs/lean_setup.md)

## License

MIT — see [LICENSE](LICENSE).

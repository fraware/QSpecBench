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

[![CI](https://github.com/fraware/QSpecBench/actions/workflows/validate.yml/badge.svg)](https://github.com/fraware/QSpecBench/actions/workflows/validate.yml)

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

## Release readiness (v1.0 targets)

| Criterion | Target | Status |
|-----------|--------|--------|
| Checked-evidence benchmarks | ≥25 | 21 (in progress) |
| Reference benchmarks | ≥18 (≥4 AI) | 18 (AI: 4) |
| AI formalization kernel anchors | 7/7 | Done |
| Semantic bridge `kernel_checked` | ≥10 | 8 (in progress) |
| OpenQASM3 gate subset + composition | RX, Toffoli, Bell scaffold | Bell scaffold done |
| README/spec maturity sync | CI enforced | Done |
| `proof_obligations` on references | All references | Done |

## Release readiness (v0.2.0 — prior release)

| Criterion | Target | Status |
|-----------|--------|--------|
| Schema v0.2 + migration guide | Done | Done |
| 44–49 benchmarks across 5 tracks | 44–49 | Done (48) |
| 8–10 reference benchmarks | 8–10 | Done (12) |
| ≥15 kernel-checked / checked evidence | ≥15 | Done |
| QCEC on equivalence track | All usable+ | Done (CI job) |
| Real SMT adapter (z3/cvc5) | 1+ benchmark | Done |
| Semantic bridge `kernel_checked` | ≥6 | Done (7) |
| Bridge CI job | verify-bridge | Done |
| Public dashboard v2 | trust levels + bridges | Done |
| Contributor docs + reference template | Done | Done |

Layer 2 baseline: 34 benchmarks, 3 references, 5 checked, zero-evidence 0.

## Release readiness (v0.1 — historical)

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

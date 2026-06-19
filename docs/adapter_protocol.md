# Adapter protocol

Adapters connect external tools to QSpecBench evidence checks.

## Active adapters (Lean-only proof assistant policy)

| Adapter | Evidence types | Trust |
|---------|----------------|-------|
| `lean/` | `lean_proof` | checked (Lean 4 kernel) |
| `bridge/` | `bridge_verify` | checked (QASM–Lean matrix alignment) |
| `sat_certificate/` | `sat_certificate` | independently_checkable |
| `smt/` | `smt_certificate` | independently_checkable |
| `qasm/` | `qasm_parse` | syntax only |
| `qec/` | `qec_verifier_result` | tool-checked |
| `python/` | `simulation` | heuristic |
| `qcec/` | `qcec_result` | externally_trusted (MQT QCEC or CLI) |
| `human_review/` | `human_review` | externally_trusted |
| `ai_formalization/` | `ai_draft` rubric | untrusted |

Coq/Rocq adapters are **not** used in this repository (see [Declined adapters](#declined-adapters)).

## Directory layout

```
adapters/<adapter_name>/
  README.md
  adapter.yaml
  check.sh
  parse_result.py
  examples/
```

## Rules

- Adapters must not silently pass
- Distinguish parse success from semantic verification
- Do not upgrade trust level beyond checker capability
- Callable from CI or documented as manual

## Declined adapters

The original mission mentioned Coq/Rocq file-existence stubs. This repository **declines** them in favor of a Lean-only proof-assistant policy:

- No `adapters/coq/` or `adapters/rocq/` directories (enforced by `tests/test_repo_policy.py`)
- Evidence types `qbricks_result` and `zx_certificate` remain schema placeholders until a driving benchmark needs a dedicated adapter

See [Lean setup](lean_setup.md) for proof assistant installation.

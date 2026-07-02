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

Coq/Rocq/Isabelle stub adapters exist for optional second-assistant evidence but are **not** in default
CI (see [Optional second-assistant adapters](#optional-second-assistant-adapters)).

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

## Optional second-assistant adapters

Lean 4 is the only kernel-checked proof assistant in **default CI**. Coq, Rocq, and Isabelle stub
adapters live under `adapters/coq/`, `adapters/rocq/`, and `adapters/isabelle/` (required by
`tests/test_repo_policy.py`) for optional evidence when `QSPECBENCH_COQ=1` and `coqc` are available
locally or in a custom CI job. They are not invoked by `.github/workflows/validate.yml` or `lint.yml`.

- Coq adapter: real `coqc` checks when enabled; see `adapters/coq/README.md`
- Rocq/Isabelle: fail-closed stubs (`skipped: true`) until a driving benchmark needs them
- Evidence types `qbricks_result` and `zx_certificate` remain schema placeholders until a dedicated adapter is needed

See [Lean setup](lean_setup.md) for proof assistant installation.

# Adapter protocol

Adapters connect external tools to QSpecBench evidence checks.

## Active adapters (Lean-only proof assistant policy)

| Adapter | Evidence types | Trust |
|---------|----------------|-------|
| `lean/` | `lean_proof` | checked (Lean 4 kernel) |
| `sat_certificate/` | `sat_certificate` | independently_checkable |
| `qasm/` | `qasm_parse` | syntax only |
| `qec/` | `qec_verifier_result` | tool-checked |
| `python/` | `simulation` | heuristic |
| `qcec/` | `qcec_result` | external (artifact check stub) |
| `smt/` | `smt_certificate` | independently_checkable |
| `ai_formalization/` | `ai_draft` rubric | untrusted |

Coq/Rocq adapters are **not** used in this repository.

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

See [Lean setup](lean_setup.md) for proof assistant installation.

# Schema migration guide (0.1 → 0.2)

QSpecBench schema **0.2** adds optional first-class fields for semantic bridges and proof obligations while remaining compatible with **0.1** specs.

## Version field

Set `qspecbench_version: "0.2"` on new benchmarks. Existing `0.1` specs continue to validate.

## New root fields

### `semantic_bridge` (optional)

Inline semantic bridge metadata (same shape as `expected/semantic_bridge.json`):

```yaml
semantic_bridge:
  artifact_gate_model: openqasm3_1q2q_clifford
  lean_module: QSpecBench.CNOT
  lean_theorem: cnot_mul_self
  normalization:
    cnot: standard_01_control_target
  claimed_link: documented_not_proved  # or kernel_checked
```

Reference benchmarks with both QASM artifacts and Lean evidence must declare a bridge (inline or `expected/semantic_bridge.json`).

When `claimed_link: kernel_checked`, a passing bridge verify evidence entry is required (`checker` containing `verify-bridge` or evidence id `bridge_verify`).

### `proof_obligations` (optional)

Named lemmas or checks that must reach `passing` (or `not_applicable`) for reference maturity:

```yaml
proof_obligations:
  - id: stabilizer_commutation
    status: passing
    notes: Lean proof wired in evidence block
  - id: decoder_correctness
    status: not_applicable
    notes: Decoder assumed per trust boundary
```

Statuses: `missing`, `partial`, `passing`, `not_applicable`.

## Existing additive fields (documented in 0.2)

- `evidence[].secondary_path` — second artifact for QCEC and similar checks (unchanged from 0.1 practice).

## Validator changes

- Reference + QASM + Lean → `semantic_bridge` required.
- `kernel_checked` → bridge verify evidence required.
- Warning (non-fatal) when `qec_status.correction_claim: checked` without passing decoder evidence noted in evidence entries.

## Migration checklist

1. Bump `qspecbench_version` to `"0.2"` when touching a spec.
2. Add `semantic_bridge` or ensure `expected/semantic_bridge.json` exists for reference claims with QASM + Lean.
3. Add `proof_obligations` when promoting to reference with multiple required lemmas.
4. Run `qspecbench validate benchmarks/` and `qspecbench check-evidence`.

See also [schema_reference.md](schema_reference.md) and [semantic_bridge.md](semantic_bridge.md).

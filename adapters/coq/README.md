# Coq proof adapter (optional kernel)

Default CI: returns `not_checked` with a clear message.

Local optional path:

```bash
export QSPECBENCH_COQ=1
coqc evidence/proof.v
python adapters/coq/parse_result.py evidence/proof.v
```

When `QSPECBENCH_COQ=1` and `coqc` is on `PATH`, the adapter runs `coqc` on the evidence file.
When the flag is unset or `coqc` is missing, the adapter fails closed with `skipped: true`.

## CNOT smoke proof (Track F)

`benchmarks/equivalence/cnot_self_inverse_cancellation/evidence/cnot_coq_smoke.v` is an
**independent** Coq proof (no axioms): CNOT as a permutation on computational-basis indices
`0..3` is self-inverse, aligned with the Lean `bridge_cnot_codegen_self_inverse` scope.

Compile locally:

```bash
export QSPECBENCH_COQ=1
coqc benchmarks/equivalence/cnot_self_inverse_cancellation/evidence/cnot_coq_smoke.v
python adapters/coq/parse_result.py \
  benchmarks/equivalence/cnot_self_inverse_cancellation/evidence/cnot_coq_smoke.v
```

Not wired into default CI evidence; optional job with `QSPECBENCH_COQ=1` only.

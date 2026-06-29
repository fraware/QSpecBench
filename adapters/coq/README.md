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

Optional smoke stub: `benchmarks/equivalence/cnot_self_inverse_cancellation/evidence/cnot_coq_smoke.v`
(compiles locally only; not wired into CI evidence).

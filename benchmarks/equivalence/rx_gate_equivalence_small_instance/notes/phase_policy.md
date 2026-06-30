# RX global phase policy (C4)

## Declared instance

`Rx(π/2)` on one qubit compared to `H` on the same wire for the fixed source/target QASM pair.

## Phase policy

- **Equivalence relation**: exact unitary equality in the complex unnormalized model used by
  QSpecBench OpenQASM3 denotation and QCEC for this benchmark.
- **Global phase**: not checked and not claimed equivalent. A scalar phase factor between
  `Rx(π/2)` and `H` is explicitly out of scope for `reference_scaffold` and blocks
  `kernel_checked_codegen_trace` until traces align on the same gate list.
- **Lean evidence**: `evidence/rx_pi2.lean` uses an H scaffold; it does not certify RX QASM
  bytes. Do not cite Lean as checking RX semantics.

## Promotion constraints

- `reference_claim` requires aligned source/target gate traces and honest
  `headline_claim_status.not_checked_under` for global phase unless a phase-aware
  equivalence relation is declared in `specification`.
- General `Rx(θ)` beyond θ = π/2 is not covered by this benchmark.

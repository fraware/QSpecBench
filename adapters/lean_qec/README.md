# Lean-QEC version-isolated distance adapter

This adapter verifies a theorem from an **exact upstream Lean-QEC commit in its own Lean toolchain**.
It does not import Lean-QEC into QSpecBench's Lean 4.14 environment and it does not reinterpret a
distance theorem as syndrome-extraction, decoder, correction, or fault-tolerance evidence.

## Concrete pilot

The checked integration manifest pins:

- repository: `https://github.com/VerifiedQC/Lean-QEC.git`;
- commit: `e0b90148694cf6b9c8482b21dbd911f2d8f13493`;
- upstream toolchain: `leanprover/lean4:v4.30.0-rc2`;
- source: `LeanQEC/Stabilizer/Examples/BB/BB90.lean`;
- source Git blob: `8414ff1fb50f888998188f6e53020e95eb7891ca`;
- theorem: `BB90_dist_10`;
- proposition supported: the BB90 CSS-code distance lower bound `10 ≤ distance`.

At the pinned source, the theorem is proved by two SAT distance obligations (`BB90_dist_z` and
`BB90_dist_x`) using LRAT-backed `bv_check`, followed by the verified SAT-to-distance translation.

## Execution

Normal corpus `check-evidence` does not silently perform a network build. Without explicit
activation, the adapter returns a structured skip. To execute the external kernel check:

```bash
QSPECBENCH_LEAN_QEC_VERIFY=1 \
  python adapters/lean_qec/parse_result.py \
  adapters/lean_qec/examples/bb90_distance_10.json
```

Verification mode:

1. creates an isolated temporary checkout;
2. fetches only the exact upstream commit;
3. checks the commit, toolchain, source Git blob identity, and theorem declaration;
4. runs `lake exe cache get` in the upstream repository;
5. builds the exact module `LeanQEC.Stabilizer.Examples.BB.BB90`;
6. emits structured JSON binding all verified identities.

## Scope discipline

A successful result can support only a **distance lower-bound** obligation. It does not support:

- syndrome-extraction circuit semantics;
- physical noise-model adequacy;
- decoder implementation correctness;
- correction/logical-state preservation;
- repeated-round/fault-tolerance behavior.

Those remain separate assurance-graph edges. This is an interoperability adapter, not the excluded
external reproduction program.

# RX global phase policy (C4)

## Claim scope

`rx_gate_equivalence_small_instance` compares RX(π/2) on qubit 0 to Hadamard under the **complex unitary** model (`qspecbench.openqasm3.complex_unitary.v1`).

## What is proved

- Lean: `bridge_rx_pi2_denotation` — `denotateOps1C rx_pi2_ops = rxGate (π/2)` entry-wise.
- Int scaffold (legacy): `bridge_rx_pi2_int_eq_h` maps π/2 RX to **unnormalized** H — documented separately.

## What is not claimed

- **Global phase equivalence** between RX(π/2) and H in the complex model (`rx_pi2_entry01_ne_hadamard_entry01` in Lean documents the mismatch).
- `kernel_checked_artifact_semantics` or codegen-trace promotion: QASM trace uses RX while early evidence used H plumbing.
- Headline promotion beyond `reference_scaffold` until manifest-bound RX trace + explicit phase policy in `semantic_bridge.normalization`.

## Promotion path

1. Align evidence QASM trace with RX gate (not H substitute).
2. Declare `normalization.global_phase` in semantic_bridge (exact / up_to_global / not_equivalent).
3. Either prove phase relation or narrow headline to matrix equality without H equivalence.

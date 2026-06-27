# Semantic bridge notes (RX gate equivalence)

## Phase convention

OpenQASM3 `rx(θ)` is denoted in Lean `ComplexGate.rxGate` with the standard rotation
`exp(-i θ X/2)` on the complex scaffold. The benchmark pair compares `rx(π/2)` on the
source artifact against `h` on the target.

`bridge_rx_pi2_eq_h` proves entry-wise equality of complex denotations:
`denotateOps1C rx_pi2_ops = hadamardC`. This is **matrix equality in ℂ**, not a
global-phase quotient: if the target were `e^{iφ} H` for φ ≠ 0, the bridge would fail.

## Why manifest binding stays blocked

1. Manifest-checked binding requires an allowlisted gate trace + theorem on that trace.
   The checked link today is RX→H denotation plumbing, not a manifest-listed RX trace
   theorem independent of H normalization.
2. Headline equivalence to H still leaves `global_phase_between_rx_and_h` unchecked if
   claims are phrased modulo global phase.

## Claimed link

`python_denotation_consistency` only (`semantic_bridge.json`). Do not promote to
`manifest_checked_theorem_binding` until obligations close honestly.

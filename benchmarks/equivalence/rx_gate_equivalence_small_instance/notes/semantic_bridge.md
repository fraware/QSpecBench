# Semantic bridge notes (RX gate equivalence)

## Phase convention

OpenQASM3 `rx(θ)` is denoted in Lean `ComplexGate.rxGate` with the standard rotation
`exp(-i θ X/2)` on the complex scaffold. The benchmark pair compares `rx(π/2)` on the
source artifact against `h` on the target.

`bridge_rx_pi2_denotation` proves complex denotation equals `rxGate (π/2)`.
`bridge_rx_pi2_int_eq_h` shows the int scaffold maps RX(π/2) to unnormalized `hadamard2`.

## Why manifest binding stays blocked

1. Manifest-checked binding requires an allowlisted gate trace + theorem on that trace.
   The checked link today is RX→H denotation plumbing, not a manifest-listed RX trace
   theorem independent of H normalization.
2. Headline equivalence to H still leaves `global_phase_between_rx_and_h` unchecked if
   claims are phrased modulo global phase.

## Claimed link

`python_denotation_consistency` only (`semantic_bridge.json`). Do not promote to
`manifest_checked_theorem_binding` until obligations close honestly.

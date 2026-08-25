# Teleportation dynamic feedforward protocol

## Claim

The on-disk teleportation-with-feedforward QASM CanonicalAst measure and if AST nodes (gates, measurements, and classical controls) are bound to the Lean Measurement.writeZOutcome / ClassicalReg feed-forward denotation under kernel-checked dynamic denotation semantics.

## Scope

Sibling of teleportation preserves state up to Pauli correction. Parent retains unitary-prefix
matrix machine closure (v2). This package binds the dynamic measure+if protocol as
CanonicalAst+denotation — never matrix KERNEL BRIDGE. Formerly labeled sibling ABRC as of
v0.2.x after a dedicated dual review of the denotation binding; **demoted for v1** to
`experimental_closed` (not gold / independently reviewed). See
`notes/dynamic_denotation_bridge_blocker.md` for promotion history.

## Checker chain

1. Fail-closed Python dynamic CanonicalAst mirror
2. verify-dynamic-denotation-bridge with denotation match true, dynamic ast match true, and matrix match false
3. Lean teleport dynamic feedforward artifact protocol linked (composes denoteCanonicalMeasures / canonicalControlsToStmts)
4. DynamicDenotationBridgeMetadata pin

## Not checked

- full OpenQASM3 dynamic circuits
- hardware semantics
- matrix KERNEL BRIDGE for measure+if

## Status

Current maturity: **experimental_closed**.

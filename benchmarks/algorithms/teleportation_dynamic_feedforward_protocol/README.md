# Teleportation dynamic feedforward protocol (sibling ABRC)

## Claim

The on-disk teleportation-with-feedforward QASM CanonicalAst measure and if AST nodes (gates, measurements, and classical controls) are bound to the Lean Measurement.writeZOutcome / ClassicalReg feed-forward denotation under kernel-checked dynamic denotation semantics.

## Scope

Sibling of teleportation preserves state up to Pauli correction. Parent retains unitary-prefix matrix ABRC (v2). This benchmark promotes the dynamic measure+if protocol as CanonicalAst+denotation ABRC — never matrix KERNEL BRIDGE. Promoted from the weaker `kernel_checked_dynamic_ast_semantics` framing after a dedicated dual review evaluated the denotation binding specifically; see `notes/dynamic_denotation_bridge_blocker.md` for the promotion history.

## Checker chain

1. Fail-closed Python dynamic CanonicalAst mirror
2. verify-dynamic-denotation-bridge with denotation match true, dynamic ast match true, and matrix match false
3. Lean teleport dynamic feedforward artifact protocol linked (composes denoteCanonicalMeasures / canonicalControlsToStmts)
4. DynamicDenotationBridgeMetadata ABRC pin

## Not checked

- full OpenQASM3 dynamic circuits
- hardware semantics
- matrix KERNEL BRIDGE for measure+if

## Status

Current maturity: **artifact_bound_reference_claim**.

# Claim diff: qiskit_optimize_1q_gates_hxx_identity

<!-- scope_fingerprint: d0b279f8eacb7e346ad278193306bc60709ed6a5d7ba3ab816eaab93b13a8b2f -->

**Maturity:** experimental_closed
**Headline status:** checked

## Informal claim (README/spec)
Under the QSpecBench OpenQASM fragment denotation, the committed H;X;X source and the target emitted by the named public compiler pass qiskit.transpiler.passes.Optimize1qGates (pinned provenance) have identical denotations. This is a concrete compiler-instance claim, not a general Qiskit correctness theorem, and it is machine-closed without independent review.

## Declared headline (claim_scope)
Under the QSpecBench OpenQASM fragment denotation, the committed H;X;X source and the Optimize1qGates target have identical denotations for this pinned compiler instance.

## Required obligations
- source_artifact_parse
- target_artifact_parse
- source_target_equivalence
- compiler_provenance

## Checked obligations
- [x] source_artifact_parse
- [x] target_artifact_parse
- [x] source_target_equivalence
- [x] compiler_provenance

## Unproved / open obligations

## Gap
- None among declared required obligations.
